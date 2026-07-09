# =====================================================================
# FILE: backend/test_multilingual_spell.py
# DESCRIPTION: Unit tests for LanguageService, TranslatorService, and SpellService.
# =====================================================================

import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the 'backend/' directory to the Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.services.language_service import LanguageService
from app.services.translator_service import TranslatorService
from app.services.spell_service import SpellService, PROTECTED_VOCABULARY

class TestMultilingualSpellServices(unittest.TestCase):
    def setUp(self):
        self.language_service = LanguageService()
        self.translator_service = TranslatorService()
        self.spell_service = SpellService()

    @patch("app.services.language_service.generate_text")
    def test_language_detection(self, mock_gen):
        # Setup mocks for language codes using robust unicode escapes to avoid windows encoding errors
        def side_effect_fn(prompt):
            # Extract the actual query part to avoid matching instructions examples
            query_part = prompt.split('Query: "')[1] if 'Query: "' in prompt else prompt
            if "\u0b27\u0b3e\u0b28" in query_part: # "ଧାନ"
                return "or"
            elif "\u0927\u093e\u0928" in query_part: # "धान"
                return "hi"
            return "en"
        mock_gen.side_effect = side_effect_fn

        # Test Hindi query
        lang_hi = self.language_service.detect_language("\u0927\u093e\u0928 \u0915\u094b \u0915\u093f\u0924\u0928\u093e \u092a\u093e\u0928\u0940 \u091a\u093e\u0939\u093f\u090f")
        self.assertEqual(lang_hi, "hi")

        # Test English query
        lang_en = self.language_service.detect_language("how much water paddy need")
        self.assertEqual(lang_en, "en")

        # Test explicit language queries
        lang_explicit_hi = self.language_service.detect_language("crop rotation in hindi")
        self.assertEqual(lang_explicit_hi, "hi")

        lang_explicit_es = self.language_service.detect_language("how much water paddy need in spanish")
        self.assertEqual(lang_explicit_es, "es")

        # Test cache hit
        with patch("app.services.language_service.generate_text") as mock_gen_cached:
            lang_hi_cached = self.language_service.detect_language("\u0927\u093e\u0928 \u0915\u094b \u0915\u093f\u0924\u0928\u093e \u092a\u093e\u0928\u0940 \u091a\u093e\u0939\u093f\u090f")
            self.assertEqual(lang_hi_cached, "hi")
            mock_gen_cached.assert_not_called()

    @patch("app.services.translator_service.ask_gemini")
    def test_translation_to_english(self, mock_ask):
        mock_ask.return_value = "How much water does paddy need?"
        
        translated = self.translator_service.translate_to_english("\u0927\u093e\u0928 \u0915\u094b \u0915\u093f\u0924\u0928\u093e \u092a\u093e\u0928\u0940 \u091a\u093e\u0939\u093f\u090f", "hi")
        self.assertEqual(translated, "How much water does paddy need?")
        mock_ask.assert_called_once()

        # Test English query bypasses translation
        mock_ask.reset_mock()
        translated_en = self.translator_service.translate_to_english("How much water does paddy need?", "en")
        self.assertEqual(translated_en, "How much water does paddy need?")
        mock_ask.assert_not_called()

    @patch("app.services.translator_service.ask_gemini")
    def test_translation_from_english(self, mock_ask):
        mock_ask.return_value = "\u0927\u093e\u0928 \u0915\u094b \u0915\u093f\u0924\u0928\u093e \u092a\u093e\u0928\u0940 \u091a\u093e\u0939\u093f\u090f"
        
        translated = self.translator_service.translate_from_english("How much water does paddy need?", "hi")
        self.assertEqual(translated, "\u0927\u093e\u0928 \u0915\u094b \u0915\u093f\u0924\u0928\u093e \u092a\u093e\u0928\u0940 \u091a\u093e\u0939\u093f\u090f")
        mock_ask.assert_called_once()

    @patch("app.services.spell_service.generate_text")
    def test_spell_correction_protects_vocab(self, mock_gen):
        mock_gen.return_value = "How much water does paddy need?"
        
        corrected = self.spell_service.correct_query("how much watr paddy need")
        self.assertEqual(corrected, "How much water does paddy need?")
        mock_gen.assert_called_once()

        for term in ["paddy", "kharif", "rabi", "azolla", "urea", "dap", "npk", "vermicompost"]:
            self.assertIn(term, PROTECTED_VOCABULARY)

if __name__ == "__main__":
    unittest.main()
