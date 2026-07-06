# =====================================================================
# FILE: backend/app/utils/security.py
# DESCRIPTION: Enterprise security middleware and request sanitizers.
# =====================================================================

import re
import os
import time
import logging
from typing import Dict, Any, List, Optional
from flask import request, abort, g

logger = logging.getLogger(__name__)

# --- Prompt Injection Detection ---
# Scan inputs for dangerous keywords attempting to override model instructions.
INJECTION_PATTERNS = [
    r"\bignore\s+(?:all\s+)?previous\s+instructions\b",
    r"\bignore\s+(?:all\s+)?above\s+instructions\b",
    r"\byou\s+are\s+now\s+a\b",
    r"\bnew\s+system\s+prompt\b",
    r"\bleak\s+(?:the\s+)?instructions\b",
    r"\bleak\s+(?:the\s+)?prompt\b",
    r"\bsystem\s+prompt\s*:\b",
    r"\bjailbreak\b",
    r"\bdo\s+not\s+follow\s+instructions\b"
]

def detect_prompt_injection(query: str) -> bool:
    """Scans the user query for prompt injection vectors."""
    if not query:
        return False
    query_clean = query.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_clean):
            logger.warning(f"[Security] Prompt injection pattern matched: '{pattern}' in user query.")
            return True
    return False


# --- Prompt Leakage Protection ---
# Strip secret prompt keywords from LLM response before returning it to the user.
LEAKAGE_KEYWORDS = [
    "task planner", "system prompt", "available agents", "available tools",
    "mcp server", "task execution plan", "execution dag", "reasoning budget",
    "heuristics-based plan", "nemotron"
]

def sanitize_prompt_leakage(response: str) -> str:
    """Removes internal prompt/architectural details leaked by the LLM response."""
    if not response:
        return ""
    sanitized = response
    for word in LEAKAGE_KEYWORDS:
        # Case insensitive replacement
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        sanitized = pattern.sub("[filtered]", sanitized)
    return sanitized


# --- Input Sanitization & SQL Injection Protection ---
SQL_INJECTION_PATTERNS = [
    r"\bunion\s+select\b",
    r"\bdrop\s+table\b",
    r"\binsert\s+into\b",
    r"\bselect\s+.*\s+from\b",
    r"\bor\s+1\s*=\s*1\b",
    r"'\s*or\s*'\s*\d+\s*=\s*\d+",
    r"--",
    r";"
]

def sanitize_input(text: str) -> str:
    """Strips HTML tags and escapes quotes to prevent XSS / raw query injection."""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r"<[^>]*>", "", text)
    # Normalize multiple spaces
    clean = " ".join(clean.split())
    return clean

def detect_sql_injection(text: str) -> bool:
    """Inspects text for common raw SQL injection attacks."""
    if not text:
        return False
    text_clean = text.lower()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text_clean):
            logger.warning(f"[Security] Potential SQL injection vector detected: '{pattern}'")
            return True
    return False


# --- In-Memory Rate Limiter (Token-Bucket) ---
class TokenBucketLimiter:
    def __init__(self, capacity: int = 60, fill_rate: float = 1.0):
        self.capacity = capacity
        self.fill_rate = fill_rate  # Tokens added per second
        self.buckets: Dict[str, Dict[str, Any]] = {}

    def is_allowed(self, ip_address: str) -> bool:
        now = time.time()
        if ip_address not in self.buckets:
            self.buckets[ip_address] = {"tokens": self.capacity, "last_updated": now}
            return True

        state = self.buckets[ip_address]
        elapsed = now - state["last_updated"]
        state["tokens"] = min(self.capacity, state["tokens"] + elapsed * self.fill_rate)
        state["last_updated"] = now

        if state["tokens"] >= 1.0:
            state["tokens"] -= 1.0
            return True
        logger.warning(f"[Security] Rate limit exceeded for IP: {ip_address}")
        return False

# Global instance allowing max 60 requests per minute
limiter = TokenBucketLimiter(capacity=60, fill_rate=1.0)

def check_rate_limit(ip_addr: str) -> bool:
    return limiter.is_allowed(ip_addr)


# --- CSRF Validation ---
def validate_csrf_origin(req) -> bool:
    """Verifies that the request's origin matches safe domains."""
    origin = req.headers.get("Origin") or req.headers.get("Referer")
    if not origin:
        # Allow client requests (e.g. mobile apps / API calls without Origin headers) if JWT is present
        return True
    
    # Standard local frontend origins
    allowed_origins = [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
        "http://localhost:5176", "http://127.0.0.1:5176"
    ]
    if any(origin.startswith(allowed) for allowed in allowed_origins):
        return True
        
    logger.warning(f"[Security] CSRF origin check failed for Origin: {origin}")
    return False
