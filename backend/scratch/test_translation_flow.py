# =====================================================================
# FILE: backend/scratch/test_translation_flow.py
# DESCRIPTION: Verification script for language prompt injection.
# =====================================================================

import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.services.response_generator import ResponseSynthesizer
from unittest.mock import patch

def run_tests():
    # 1. Hindi test
    with patch('app.services.response_generator.generate_text') as mock_gen:
        mock_gen.return_value = "Mocked Hindi response"
        
        ResponseSynthesizer.synthesize_response(
            query="Should I irrigate today?",
            context={"location": "Delhi"},
            preferred_language="hi",
            stream=False
        )
        
        called_prompt = mock_gen.call_args[0][0]
        assertion_hi = "CRITICAL: The user's preferred interface language is Hindi." in called_prompt
        print(f"[-] Hindi instructions injected correctly: {assertion_hi}")
        assert assertion_hi, "Hindi prompt instruction injection failed!"

    # 2. Odia test
    with patch('app.services.response_generator.generate_text') as mock_gen:
        mock_gen.return_value = "Mocked Odia response"
        
        ResponseSynthesizer.synthesize_response(
            query="Should I irrigate today?",
            context={"location": "Bhubaneswar"},
            preferred_language="or",
            stream=False
        )
        
        called_prompt = mock_gen.call_args[0][0]
        assertion_or = "CRITICAL: The user's preferred interface language is Odia." in called_prompt
        print(f"[-] Odia instructions injected correctly: {assertion_or}")
        assert assertion_or, "Odia prompt instruction injection failed!"

    print("[SUCCESS] All language prompt injection tests passed!")

if __name__ == "__main__":
    run_tests()
