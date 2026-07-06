# =====================================================================
# FILE: backend/app/services/translator_service.py
# DESCRIPTION: Translation service that handles translating queries to English
#              and translating responses back to target languages with caching and fallbacks.
# =====================================================================

import logging
from threading import Lock
from typing import Dict, Tuple
from app.services.gemini_service import ask_gemini


logger = logging.getLogger(__name__)

# Map ISO 639-1 language codes to full names for prompting
LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "gu": "Gujarati",
    "mr": "Marathi",
    "ur": "Urdu",
    "ne": "Nepali",
    "si": "Sinhala",
    "ar": "Arabic",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "pt": "Portuguese",
    "it": "Italian",
    "nl": "Dutch",
    "ru": "Russian",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "ja": "Japanese",
    "ko": "Korean",
    "th": "Thai",
    "vi": "Vietnamese",
    "tr": "Turkish",
    "fa": "Persian",
    "he": "Hebrew",
    "id": "Indonesian",
    "ms": "Malay",
    "sw": "Swahili",
    "pl": "Polish",
    "uk": "Ukrainian",
    "ro": "Romanian",
    "hu": "Hungarian",
    "cs": "Czech",
    "el": "Greek",
    "fi": "Finnish",
    "no": "Norwegian",
    "sv": "Swedish",
    "da": "Danish",
    "is": "Icelandic",
    "fil": "Filipino",
    "af": "Afrikaans",
    "zu": "Zulu",
    "or": "Odia"
}


STATIC_TRANSLATIONS = {
    "hi": {
        "👋 Hello! I'm AgriAgent AI. How can I help you today?": "👋 नमस्ते! मैं AgriAgent AI हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
        "👋 Good morning! I'm AgriAgent AI. How can I help you today?": "👋 सुप्रभात! मैं AgriAgent AI हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
        "👋 Good afternoon! I'm AgriAgent AI. How can I help you today?": "👋 शुभ दोपहर! मैं AgriAgent AI हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
        "👋 Good evening! I'm AgriAgent AI. How can I help you today?": "👋 शुभ संध्या! मैं AgriAgent AI हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
        "🌾 I'm AgriAgent AI. I can help with crops, weather, irrigation, and plant disease diagnosis.": "🌾 मैं AgriAgent AI हूँ। मैं फसलों, मौसम, सिंचाई और पौधों की बीमारी की पहचान में मदद कर सकता हूँ।",
        "😊 You're welcome! Let me know if you need anything else.": "😊 आपका स्वागत है! अगर आपको कुछ और चाहिए तो बताइए।",
        "👋 Goodbye! Have a great day and happy farming! 🌾": "👋 अलविदा! आपका दिन शुभ हो और खेती मंगलमय हो! 🌾",
        "Please upload a crop leaf image.": "कृपया फसल के पत्ते की तस्वीर अपलोड करें।",
        "Generating recommendation...": "सिफारिश तैयार की जा रही है...",
        "Thinking...": "सोच रहा हूँ..."
    },
    "or": {
        "👋 Hello! I'm AgriAgent AI. How can I help you today?": "👋 ନମସ୍କାର! ମୁଁ AgriAgent AI। ଆଜି ମୁଁ ଆପଣଙ୍କୁ କିପରି ସହାୟତା କରିପାରିବି?",
        "👋 Good morning! I'm AgriAgent AI. How can I help you today?": "👋 ସୁପ୍ରଭାତ! ମୁଁ AgriAgent AI। ଆଜି ମୁଁ ଆପଣଙ୍କୁ କିପରି ସହାୟତା କରିପାରିବି?",
        "👋 Good afternoon! I'm AgriAgent AI. How can I help you today?": "👋 ଶୁଭ ଅପରାହ୍ନ! ମୁଁ AgriAgent AI। ଆଜି ମୁଁ ଆପଣଙ୍କୁ କିପରି ସହାୟତା କରିପାରିବି?",
        "👋 Good evening! I'm AgriAgent AI. How can I help you today?": "👋 ଶୁଭ ସନ୍ଧ୍ୟା! ମୁଁ AgriAgent AI। ଆଜି ମୁଁ ଆପଣଙ୍କୁ କିପରି ସହାୟତା କରିପାରିବି?",
        "🌾 I'm AgriAgent AI. I can help with crops, weather, irrigation, and plant disease diagnosis.": "🌾 ମୁଁ AgriAgent AI। ମୁଁ ଫସଲ, ପାଣିପାଗ, ସିଚାଇ ଏବଂ ଗଛର ରୋଗ ଚିହ୍ନଟରେ ସହାୟତା କରିପାରିବି।",
        "😊 You're welcome! Let me know if you need anything else.": "😊 ଆପଣଙ୍କୁ ସ୍ୱାଗତ! ଆଉ କିଛି ଦରକାର ହେଲେ ଜଣାନ୍ତୁ।",
        "👋 Goodbye! Have a great day and happy farming! 🌾": "👋 ବିଦାୟ! ଆପଣଙ୍କ ଦିନ ଭଲ କଟୁ ଏବଂ ଚାଷ ଶୁଭ ହେଉ! 🌾",
        "Please upload a crop leaf image.": "ଦୟାକରି ଫସଲ ପତ୍ରର ଫଟୋ ଅପଲୋଡ୍ କରନ୍ତୁ।",
        "Generating recommendation...": "ପରାମର୍ଶ ପ୍ରସ୍ତୁତ କରୁଛି...",
        "Thinking...": "ଚିନ୍ତା କରୁଛି..."
    }
}
class TranslatorService:
    """
    Translates text between English and target languages.
    Implements translation caching to minimize LLM API calls.
    """
    def __init__(self):
        self._cache: Dict[Tuple[str, str], str] = {}
        self._lock = Lock()

    def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translates a user query from source_lang to English."""
        if not text or not text.strip():
            return ""

        if source_lang == "en":
            return text

        clean_text = text.strip()
        cache_key = (clean_text.lower(), "en")

        with self._lock:
            if cache_key in self._cache:
                logger.info(f"Translation cache hit (to English) for '{clean_text[:30]}...'")
                return self._cache[cache_key]

        prompt = f"""You are a professional agricultural translator.
Translate the following query into clear, natural English.
Preserve the context, intention, and all agricultural terms.
Do not explain, do not add any comments, and return ONLY the English translation.

Query:
{clean_text}
"""
        translated_text = clean_text
        try:
            logger.info(f"Translating to English from {source_lang}: '{clean_text[:50]}'")
            response = ask_gemini(prompt, temperature=0.1).strip()
            if response and not response.lower().startswith("error"):
                translated_text = response
                logger.info(f"Translated query: '{translated_text}'")
            else:
                logger.warning(f"Translation returned invalid response: {response}")
        except Exception as e:
            logger.error(f"Translation to English failed: {e}. Falling back to original text.")


        with self._lock:
            self._cache[cache_key] = translated_text

        return translated_text

    def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translates synthesized response from English to target_lang."""
        if not text or not text.strip():
            return ""

        if target_lang == "en":
            return text

        clean_text = text.strip()
        static_translation = STATIC_TRANSLATIONS.get(target_lang, {}).get(clean_text)
        if static_translation:
            return static_translation
        cache_key = (clean_text.lower(), target_lang)

        with self._lock:
            if cache_key in self._cache:
                logger.info(f"Translation cache hit (from English) for target: {target_lang}")
                return self._cache[cache_key]

        target_lang_name = LANGUAGE_MAP.get(target_lang, target_lang)
        prompt = f"""You are a professional translator.
Translate the following English agricultural advisory response into {target_lang_name}.
Ensure the tone remains professional, expert, and direct.
CRITICAL:
1. Maintain all markdown formatting, list structures, line breaks, bold text, and agricultural emojis (e.g. 🌿, 🌾, 🚜, 🌦, 📍, 🌡, ☁, 🦠, 🌱, ⚠) EXACTLY as they are in the original text.
2. Do not translate or change standard agricultural shortnames like DAP, NPK, N-P-K, etc.
3. Do not add any conversational remarks, warnings about translation, or introductory/concluding text. Return ONLY the translated response.

Text to translate:
{clean_text}
"""
        translated_text = clean_text
        try:
            logger.info(f"Translating response from English to {target_lang_name}")
            response = ask_gemini(prompt, temperature=0.1).strip()
            if response and not response.lower().startswith("error"):
                translated_text = response
            else:
                logger.warning(f"Translation from English returned invalid response: {response}")
        except Exception as e:
            logger.error(f"Translation from English failed: {e}. Falling back to original text.")


        with self._lock:
            self._cache[cache_key] = translated_text

        return translated_text

# Global instance
translator_service = TranslatorService()
