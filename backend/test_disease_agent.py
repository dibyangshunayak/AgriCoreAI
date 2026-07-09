# =====================================================================
# FILE: backend/test_disease_agent.py
# DESCRIPTION: A testing script that verifies the complete Disease Detection
#              Agent pipeline, including generating a mock diseased leaf image,
#              validating it, and querying Gemini for recommendations.
# =====================================================================

# --- Imports Section ---
# 'sys' allows us to modify the system path to resolve app-level imports.
import sys

# 'os' allows us to create folders and delete mock files after tests.
import os

# 'Path' from 'pathlib' handles filesystem operations elegantly.
from pathlib import Path

# 'Image' and 'ImageDraw' from 'PIL' are used to dynamically construct a mock image.
# This prevents the test from failing if you don't have a real leaf photo on your disk.
from PIL import Image, ImageDraw

# Add the parent directory (backend/) to the system path so Python can resolve imports from 'app.'
# Path(__file__) is backend/test_disease_agent.py.
# .resolve() gets the absolute canonical path.
# .parent gets the backend/ folder.
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

# Import the main workflow function from our disease agent.
from app.agents.disease_agent import detect_crop_disease

def create_mock_leaf_image(output_path: Path) -> None:
    """
    Generates a synthetic mock leaf image with a visible "disease spot"
    using Pillow. This ensures the integration test is completely self-contained.

    Parameters:
        output_path (Path): The path where the mock image should be saved.
    """
    print(f"[+] Creating a mock diseased leaf image at: {output_path}")

    # Ensure the parent directory (uploads/leaf_images/) exists.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Create a base canvas (300x300 pixels) with a dark green color (representing a leaf).
    # RGB color (34, 139, 34) is Forest Green.
    img = Image.new("RGB", (300, 300), color=(34, 139, 34))

    # 2. Get a drawing context to draw shapes on top of the image canvas.
    draw = ImageDraw.Draw(img)

    # 3. Draw a mock yellow/brown disease spot in the middle of the leaf.
    # We draw an ellipse from coordinates (100, 100) to (200, 200).
    # RGB color (218, 165, 32) is Goldenrod, which looks like a yellow blight spot.
    draw.ellipse([100, 100, 200, 200], fill=(218, 165, 32))

    # 4. Save the generated image as a JPEG.
    img.save(output_path, "JPEG")
    print("[+] Mock image generated successfully.")

def run_test() -> None:
    """
    Orchestrates the verification process:
    1. Reconfigures console encoding (helps display emojis on Windows Command Prompt/PowerShell).
    2. Creates a mock leaf image.
    3. Triggers the Crop Disease Detection Agent.
    4. Prints the output.
    """
    # Fix Windows terminal encoding for emojis (UTF-8)
    # Emojis like 🌿, 🔍, 💊, 🛡, 📊 might display as garbled characters on standard cmd otherwise.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("\n" + "="*60)
    print("AGRICORE AI: TESTING DISEASE DETECTION AGENT")
    print("="*60)

    # Define the mock image file path inside the uploads/leaf_images/ directory.
    mock_image_path = BACKEND_DIR / "uploads" / "leaf_images" / "mock_diseased_leaf.jpg"

    # Make sure we generate the mock image before calling the agent.
    try:
        create_mock_leaf_image(mock_image_path)
    except Exception as e:
        print(f"[-] Failed to create mock image: {e}")
        return

    # Call the disease agent inside a try-except block to handle failures gracefully.
    print(f"\n[1] Querying Disease Detection Agent for image: {mock_image_path}...\n")
    print("Waiting for Google Gemini Vision API to analyze image...")

    try:
        # Run the detection workflow.
        # This will load, validate, read bytes, and query Gemini Vision.
        result = detect_crop_disease(str(mock_image_path))

        print("\n" + "="*60)
        print("DISEASE AGENT ANALYSIS RESULT:")
        print("="*60)
        print(result)
        print("="*60 + "\n")
        print("[+] Test completed successfully!")

    except Exception as e:
        # If any step fails, print a descriptive error message with the traceback.
        print("\n" + "="*60)
        print(f"[-] Test failed with exception: {e}")
        print("="*60 + "\n")

if __name__ == "__main__":
    run_test()
