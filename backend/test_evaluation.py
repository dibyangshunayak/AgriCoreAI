# =====================================================================
# FILE: backend/test_evaluation.py
# DESCRIPTION: E2E pipeline validation and evaluation tests for AgriCore AI.
#              Tests language detection, translation, spelling correction, intent routing,
#              RAG lookup, and final translation back.
# =====================================================================

import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the 'backend/' directory to the Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.agents.coordinator_agent import process_request, process_request_stream

class TestAgriCoreEvaluation(unittest.TestCase):

    @patch("app.agents.coordinator_agent.language_service.detect_language")
    @patch("app.agents.coordinator_agent.translator_service.translate_to_english")
    @patch("app.agents.coordinator_agent.spell_service.correct_query")
    @patch("app.agents.coordinator_agent.translator_service.translate_from_english")
    @patch("app.agents.coordinator_agent.generate_execution_plan")
    @patch("app.agents.coordinator_agent.RAGService.retrieve_context")
    @patch("app.agents.coordinator_agent.get_crop_recommendation")
    @patch("app.agents.coordinator_agent.ResponseSynthesizer.synthesize_response")
    def test_pipeline_hindi_query(self, mock_synth, mock_crop, mock_rag, mock_plan, mock_trans_from, mock_correct, mock_trans_to, mock_detect):
        # 1. Setup mocks for: "धान को कितना पानी चाहिए"
        mock_detect.return_value = "hi"
        mock_trans_to.return_value = "how much water does paddy need"
        mock_correct.return_value = "How much water does paddy need?"
        mock_plan.return_value = {
            "steps": [{"step": 1, "agent": "crop", "action": "irrigation guidelines"}],
            "required_data": [],
            "response_tone": "scientific"
        }
        mock_rag.return_value = "Paddy crops require 1200-1500 mm water per season."
        mock_crop.return_value = "Paddy needs standing water of 2-5 cm."
        mock_synth.return_value = "Paddy requires substantial water (1200-1500 mm). Maintain 2-5 cm of water."
        mock_trans_from.return_value = "धान को लगभग 1200-1500 मिमी पानी की आवश्यकता होती है।"

        # 2. Run process_request
        response = process_request("धान को कितना पानी चाहिए")

        # 3. Assertions
        mock_detect.assert_called_once_with("धान को कितना पानी चाहिए")
        mock_trans_to.assert_called_once_with("धान को कितना पानी चाहिए", "hi")
        mock_correct.assert_called_once_with("how much water does paddy need")
        mock_plan.assert_called_once_with(
            user_query="How much water does paddy need?",
            image_uploaded=False,
            gps_available=False,
            location_name=None,
            conversation_context=None
        )
        mock_rag.assert_called_once_with("How much water does paddy need?")
        mock_synth.assert_called_once()
        mock_trans_from.assert_called_once_with(
            "Paddy requires substantial water (1200-1500 mm). Maintain 2-5 cm of water.", "hi"
        )
        
        self.assertEqual(response["recommendation"], "धान को लगभग 1200-1500 मिमी पानी की आवश्यकता होती है।")
        self.assertIn("crop_agent", response["agents_used"])

    @patch("app.agents.coordinator_agent.language_service.detect_language")
    @patch("app.agents.coordinator_agent.translator_service.translate_to_english")
    @patch("app.agents.coordinator_agent.spell_service.correct_query")
    @patch("app.agents.coordinator_agent.translator_service.translate_from_english")
    @patch("app.agents.coordinator_agent.generate_execution_plan")
    @patch("app.agents.coordinator_agent.RAGService.retrieve_context")
    @patch("app.agents.coordinator_agent.get_crop_recommendation")
    @patch("app.agents.coordinator_agent.ResponseSynthesizer.synthesize_response")
    def test_pipeline_english_query_with_spelling_error(self, mock_synth, mock_crop, mock_rag, mock_plan, mock_trans_from, mock_correct, mock_trans_to, mock_detect):
        # 1. Setup mocks for: "how much watr paddy need"
        mock_detect.return_value = "en"
        mock_trans_to.return_value = "how much watr paddy need"
        mock_correct.return_value = "How much water does paddy need?"
        mock_plan.return_value = {
            "steps": [{"step": 1, "agent": "crop", "action": "irrigation guidelines"}],
            "required_data": [],
            "response_tone": "scientific"
        }
        mock_rag.return_value = "Paddy crops require 1200-1500 mm water per season."
        mock_crop.return_value = "Paddy needs standing water of 2-5 cm."
        mock_synth.return_value = "Paddy requires substantial water. Maintain 2-5 cm."
        # No back-translation needed for English, returns original synthesized response
        mock_trans_from.side_effect = lambda text, lang: text

        # 2. Run process_request
        response = process_request("how much watr paddy need")

        # 3. Assertions
        mock_detect.assert_called_once_with("how much watr paddy need")
        mock_trans_to.assert_called_once_with("how much watr paddy need", "en")
        mock_correct.assert_called_once_with("how much watr paddy need")
        
        self.assertEqual(response["recommendation"], "Paddy requires substantial water. Maintain 2-5 cm.")
        self.assertIn("crop_agent", response["agents_used"])

    @patch("app.agents.coordinator_agent.language_service.detect_language")
    @patch("app.agents.coordinator_agent.translator_service.translate_to_english")
    @patch("app.agents.coordinator_agent.spell_service.correct_query")
    @patch("app.agents.coordinator_agent.translator_service.translate_from_english")
    @patch("app.agents.coordinator_agent.generate_execution_plan")
    @patch("app.agents.coordinator_agent.RAGService.retrieve_context")
    @patch("app.agents.coordinator_agent.get_crop_recommendation")
    @patch("app.agents.coordinator_agent.ResponseSynthesizer.synthesize_response")
    def test_pipeline_stream_french_query(self, mock_synth, mock_crop, mock_rag, mock_plan, mock_trans_from, mock_correct, mock_trans_to, mock_detect):
        # 1. Setup mocks for streaming French query: "De combien d'eau le riz a-t-il besoin"
        mock_detect.return_value = "fr"
        mock_trans_to.return_value = "how much water paddy need"
        mock_correct.return_value = "How much water does paddy need?"
        mock_plan.return_value = {
            "steps": [{"step": 1, "agent": "crop", "action": "irrigation guidelines"}],
            "required_data": [],
            "response_tone": "scientific"
        }
        mock_rag.return_value = "Paddy crops require 1200-1500 mm water per season."
        mock_crop.return_value = "Paddy needs standing water of 2-5 cm."
        mock_synth.return_value = "Paddy needs water."
        mock_trans_from.return_value = "Le riz a besoin d'eau."

        # Run stream
        generator = process_request_stream("De combien d'eau le riz a-t-il besoin")
        output_tokens = list(generator)

        # Assertions
        mock_detect.assert_called_once_with("De combien d'eau le riz a-t-il besoin")
        mock_trans_to.assert_called_once_with("De combien d'eau le riz a-t-il besoin", "fr")
        mock_correct.assert_called_once_with("how much water paddy need")
        mock_synth.assert_called_once()
        mock_trans_from.assert_called_once_with("Paddy needs water.", "fr")
        
        # Reconstruct the string from yielded characters
        reconstructed = "".join(output_tokens)
        self.assertEqual(reconstructed, "Le riz a besoin d'eau.")

if __name__ == "__main__":
    unittest.main()
