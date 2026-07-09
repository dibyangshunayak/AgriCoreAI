# =====================================================================
# FILE: backend/app/agents/disease_agent.py
# DESCRIPTION: Disease Detection Agent using NVIDIA Vision API
#              (nvidia/nemotron-nano-12b-v2-vl) instead of Gemini.
# =====================================================================

import logging
from typing import Dict, Any

from app.services.image_service import read_image, ImageServiceError
from app.services.nvidia_service import analyze_image_with_nvidia

logger = logging.getLogger(__name__)


class DiseaseAgentException(Exception):
    """Custom exception for the Disease Detection Agent."""
    pass


def detect_crop_disease(image_path: str) -> str:
    """
    Reads a crop leaf image and sends it to NVIDIA's vision model for
    agronomic disease analysis.

    Parameters:
        image_path (str): Path to the crop leaf image file.

    Returns:
        str: Structured disease analysis report.

    Raises:
        DiseaseAgentException: On image loading or model invocation failure.
    """
    logger.info(f"Initiating NVIDIA crop disease analysis for: {image_path}")

    # ── Step 1: Load & Validate Image ────────────────────────────────
    try:
        image_data = read_image(image_path)
        image_bytes = image_data["bytes"]
        mime_type = image_data["mime_type"]
        logger.info(f"Image validated. MIME: {mime_type}, Size: {len(image_bytes)} bytes")
    except ImageServiceError as e:
        logger.error(f"Image validation failed: {e}", exc_info=True)
        raise DiseaseAgentException(f"Image preparation failed: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error reading image {image_path}: {e}", exc_info=True)
        raise DiseaseAgentException(f"Unexpected image reading error: {e}") from e

    # ── Step 2: Build Prompt ──────────────────────────────────────────
    prompt = """You are AgriCore AI, a professional agronomic disease diagnosis assistant.

First determine whether the uploaded image is a real crop leaf.
If the image is blurry, is not a leaf, contains drawings, or is poorly illuminated, return EXACTLY:

❌ Image Validation Failed

Reason:
[Specify the exact reason professionally, e.g. "The image is too blurry", "The image does not depict a plant leaf"]

Please upload:
✅ A close-up image of one leaf
✅ Good lighting
✅ Sharp focus
✅ Minimal background

Otherwise analyze the leaf and return EXACTLY (do not output any markdown code blocks, introductory text, or concluding remarks):

🌿 Disease:
[Name of disease or "Healthy Leaf"]

🦠 Cause:
[Identify the pathogen or factor causing this disease]

🔍 Symptoms:
[Provide a professional description of visible symptoms and lesions]

💊 Treatment:
[Practical and professional treatment recommendations, including chemical or cultural controls]

🛡 Prevention:
[Agronomic prevention strategies, such as crop rotation or sanitization]

📊 Confidence:
[Must be exactly one of: Low / Medium / High]

Rules:
1. Maximum 150 words total.
2. Use professional agricultural language.
3. Express scientific uncertainty where appropriate.
4. Do not invent diseases.
5. Provide practical, action-oriented recommendations."""

    # ── Step 3: Call NVIDIA Vision API ───────────────────────────────
    logger.info("Submitting multimodal payload to NVIDIA Vision API...")
    try:
        result = analyze_image_with_nvidia(image_bytes, mime_type, prompt)
        if not result:
            raise DiseaseAgentException("NVIDIA Vision API returned an empty response.")
        logger.info("Crop disease analysis via NVIDIA completed successfully.")
        return result
    except Exception as e:
        logger.error(f"NVIDIA Vision API invocation failed: {e}", exc_info=True)
        raise DiseaseAgentException(f"Failed to communicate with AI model: {e}") from e
