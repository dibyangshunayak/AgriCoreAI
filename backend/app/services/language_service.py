# =====================================================================
# FILE: backend/app/services/language_service.py
# DESCRIPTION: Language detection service that detects the query language
#              using NVIDIA Nemotron with caching.
# =====================================================================

import logging
from threading import Lock
from typing import Dict
from app.services.nvidia_service import generate_text


logger = logging.getLogger(__name__)

class LanguageService:
    """
    Detects the primary user language of a query.
    Utilizes caching to optimize performance and minimize API overhead.
    """
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._lock = Lock()

    def detect_language(self, text: str) -> str:
        """
        Detects user query language.
        Returns the two-letter ISO 639-1 code (e.g., 'en', 'hi', 'or', 'ja', 'fr', 'es').
        Mixed-language queries containing a major Indian language (e.g. Hindi or Odia)
        mixed with English terms should resolve to that Indian language (e.g., 'hi' or 'or').
        """
        if not text or not text.strip():
            return "en"

        clean_text = text.strip()
        
        # Check for explicit language requests in the text (e.g. "in hindi", etc.)
        text_lower = clean_text.lower()
        explicit_lang_map = {
            "hindi": "hi",
            "japanese": "ja",
            "french": "fr",
            "spanish": "es",
            "english": "en"
        }
        
        # Regex patterns to find explicit language requests
        pattern_indicator = r'\b(?:in|tell\s+in|explain\s+in|reply\s+in|translate\s+to|write\s+in|speak\s+in|into|to|through)\s+(hindi|japanese|french|spanish|english)\b'
        pattern_end = r'(?:[,;:\-\s]|^)(hindi|japanese|french|spanish|english)\s*$'
        
        import re
        match_ind = re.search(pattern_indicator, text_lower)
        match_end = re.search(pattern_end, text_lower)
        
        explicit_lang = None
        if match_ind:
            explicit_lang = match_ind.group(1)
        elif match_end:
            explicit_lang = match_end.group(1)
            
        if explicit_lang:
            lang_code = explicit_lang_map[explicit_lang]
            logger.info(f"Explicit language request detected: {explicit_lang} -> {lang_code}")
            return lang_code

        # Check if the query is purely English / ASCII to bypass LLM call
        is_pure_english = True
        try:
            clean_text.encode("ascii")
        except UnicodeEncodeError:
            is_pure_english = False

        if is_pure_english:
            logger.info("Language detection bypassed (English ASCII check): en")
            return "en"

        cache_key = clean_text.lower()

        # Check cache
        with self._lock:
            if cache_key in self._cache:
                logger.info(f"Language cache hit for '{clean_text[:30]}...': {self._cache[cache_key]}")
                return self._cache[cache_key]

        # Call LLM for detection
        prompt = f"""Identify the primary language of the user query below.
Respond with ONLY the two-letter ISO 639-1 language code (e.g. 'en', 'hi', 'ja', 'fr', 'es').
For mixed language queries, identify the primary non-English language if present (e.g. if the user says 'धान cultivation process', identify 'hi' for Hindi).
If the text is purely English, respond with 'en'.
Do not include punctuation, explanations, markdown, or any other text.

Query: "{clean_text}"
ISO 639-1 Code:"""

        lang_code = "en"
        try:
            logger.info(f"Detecting language for: '{clean_text[:50]}'")
            response = generate_text(prompt).strip().lower()
            
            # Extract 2 letter code if response is long or contains noise
            cleaned = "".join([c for c in response if c.isalnum()]).strip()
            if len(cleaned) >= 2:
                lang_code = cleaned[:2]
            else:
                lang_code = "en"
                
            logger.info(f"Detected language (NVIDIA): {lang_code}")
        except Exception as e:
            logger.error(f"NVIDIA language detection failed: {e}. Defaulting to 'en'.")
            lang_code = "en"


        # Validate language code
        supported_langs = {
            "en", "hi", "bn", "te", "ta", "kn", "ml", "pa", "gu", "mr", "ur", "ne", "si", "ar", "fr",
            "de", "es", "pt", "it", "nl", "ru", "zh-CN", "zh-TW", "ja", "ko", "th", "vi", "tr", "fa",
            "he", "id", "ms", "sw", "pl", "uk", "ro", "hu", "cs", "el", "fi", "no", "sv", "da", "is",
            "fil", "af", "zu", "or"
        }
        if lang_code not in supported_langs:
            # Check prefix (e.g. 'zh' for 'zh-CN') or fallback
            matched = False
            for supported in supported_langs:
                if lang_code.startswith(supported) or supported.startswith(lang_code):
                    lang_code = supported
                    matched = True
                    break
            if not matched:
                lang_code = "en"

        # Save to cache
        with self._lock:
            self._cache[cache_key] = lang_code

        return lang_code

# Global instance
language_service = LanguageService()


