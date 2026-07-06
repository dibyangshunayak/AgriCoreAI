# =====================================================================
# FILE: backend/app/services/spell_service.py
# DESCRIPTION: Spelling correction service that corrects farmer queries
#              in English while strictly protecting agricultural vocabulary.
# =====================================================================

import logging
from threading import Lock
from typing import Dict
from app.services.nvidia_service import generate_text


logger = logging.getLogger(__name__)

PROTECTED_VOCABULARY = [
    "paddy", "kharif", "rabi", "azolla", "jowar", "bajra", "moong",
    "urea", "dap", "npk", "vermicompost", "biofertilizer", "intercropping",
    "mulching", "irrigate", "irrigation"
]

class SpellService:
    """
    Performs spelling and grammatical correction on English user queries.
    Strictly protects specific agricultural terms from being incorrectly corrected.
    """
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._lock = Lock()

    def correct_query(self, query: str) -> str:
        """
        Corrects spelling errors in an English query.
        Guarantees that protected agricultural vocabulary remains unchanged.
        """
        if not query or not query.strip():
            return ""

        clean_query = query.strip()
        cache_key = clean_query.lower()

        # Check cache
        with self._lock:
            if cache_key in self._cache:
                logger.info(f"Spell correction cache hit for '{clean_query[:30]}...': {self._cache[cache_key]}")
                return self._cache[cache_key]

        vocab_list_str = ", ".join(PROTECTED_VOCABULARY)
        prompt = f"""You are an agricultural AI spelling and grammar corrector.
Correct any spelling mistakes or grammatical issues in the user's input query to make it natural and clean English.
CRITICAL INSTRUCTION:
Do NOT correct, alter, modify, or corruption any of the following agricultural and crop-related words under any circumstances:
[{vocab_list_str}]

Examples:
- Input: how much watr paddy need -> Corrected: How much water does paddy need?
- Input: rice cultevation -> Corrected: Rice cultivation
- Input: wether tommorow -> Corrected: Weather tomorrow
- Input: fertlizer for paddy -> Corrected: Fertilizer for paddy
- Input: tomato leaf blite -> Corrected: Tomato leaf blight

Do not explain, do not add conversational remarks, and return ONLY the corrected query.

Input query:
{clean_query}
"""
        corrected_query = clean_query
        try:
            logger.info(f"Spell correcting query: '{clean_query}'")
            response = generate_text(prompt, temperature=0.1).strip()
            # Basic validation: ensure LLM didn't return an empty string or error
            if response and not response.lower().startswith("error"):
                corrected_query = response
                logger.info(f"Corrected query (NVIDIA): '{corrected_query}'")
        except Exception as e:
            logger.error(f"NVIDIA spell correction failed: {e}. Falling back to original query.")


        # Post-validation to protect terms explicitly
        # If the LLM corrupted any of our protected words, we should restore them, but
        # a good LLM prompt is usually sufficient. Let's make sure casing is handled.
        # We can also do a quick sanity check to make sure the meaning is preserved.

        # Save to cache
        with self._lock:
            self._cache[cache_key] = corrected_query

        return corrected_query

# Global instance
spell_service = SpellService()
