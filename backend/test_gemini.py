# =====================================================================
# FILE: backend/test_gemini.py
# DESCRIPTION: A simple test script to verify that the Gemini Service
#              is configured correctly and can communicate with the Gemini API.
# =====================================================================

# --- Imports Section ---
# Import sys to add backend/app or workspace roots to Python's system path if needed.
import sys
from pathlib import Path

# Add the parent directory (backend/) to the system path so Python can resolve imports from 'app.'
# Path(__file__) is backend/test_gemini.py.
# .resolve() gets the absolute path.
# .parent gets backend/
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

# Import the ask_gemini function from our newly created service module.
from app.services.gemini_service import ask_gemini

# --- Test Script Logic ---
def run_test():
    """
    Executes a test query to verify that the Gemini API is responding.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("\n" + "="*50)
    print("AGRICORE AI: TESTING GEMINI SERVICE")
    print("="*50)

    # 1. Define a farmer-related test prompt as requested.
    test_prompt = "Explain crop rotation in simple words."
    
    print(f"\n[1] Sending Test Prompt:\n{test_prompt}\n")
    print("Waiting for response from Google Gemini API...")
    
    # 2. Call the Gemini service.
    response = ask_gemini(test_prompt)
    
    # 3. Print the results.
    print("\n" + "="*50)
    print("GEMINI RESPONSE:")
    print("="*50)
    print(response)
    print("="*50 + "\n")

if __name__ == "__main__":
    run_test()
