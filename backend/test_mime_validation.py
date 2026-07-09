# =====================================================================
# FILE: backend/test_mime_validation.py
# DESCRIPTION: Test suite to verify content-based MIME validation on file
#              uploads and that non-image files do not trigger disease routing.
# =====================================================================

import os
import sys
import unittest
import json
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add 'backend/' directory to the Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.main import create_app
from app.services.image_service import is_image_file
from app.agents.coordinator_agent import process_request

class TestMimeValidationAndRouting(unittest.TestCase):
    """
    Verifies that only valid images (.jpg, .jpeg, .png, .webp) pass MIME validation,
    spoofed files are rejected, and non-image files do not trigger disease routing.
    """

    def setUp(self) -> None:
        self.app = create_app()
        self.client = self.app.test_client()
        self.test_upload_dir = BACKEND_DIR / "uploads"
        self.test_upload_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        # Clean up files created during the test
        for file in self.test_upload_dir.glob("temp_test_*"):
            try:
                file.unlink()
            except OSError:
                pass

    def test_image_service_is_image_file(self) -> None:
        """Test is_image_file helper function with various content and extensions."""
        # 1. Valid JPEG
        jpeg_path = self.test_upload_dir / "temp_test_valid.jpg"
        with open(jpeg_path, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01")
        self.assertTrue(is_image_file(str(jpeg_path)))

        # 2. Valid PNG
        png_path = self.test_upload_dir / "temp_test_valid.png"
        with open(png_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
        self.assertTrue(is_image_file(str(png_path)))

        # 3. Valid WEBP
        webp_path = self.test_upload_dir / "temp_test_valid.webp"
        with open(webp_path, "wb") as f:
            f.write(b"RIFF\x14\x00\x00\x00WEBPVP8L")
        self.assertTrue(is_image_file(str(webp_path)))

        # 4. Invalid PDF (even if named with an image extension)
        bad_jpg_path = self.test_upload_dir / "temp_test_spoofed.jpg"
        with open(bad_jpg_path, "wb") as f:
            f.write(b"%PDF-1.4\n%...")
        self.assertFalse(is_image_file(str(bad_jpg_path)))

        # 5. PDF with PDF extension
        pdf_path = self.test_upload_dir / "temp_test_valid.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%...")
        self.assertFalse(is_image_file(str(pdf_path)))

        # 6. CSV file
        csv_path = self.test_upload_dir / "temp_test_valid.csv"
        with open(csv_path, "wb") as f:
            f.write(b"header1,header2\nvalue1,value2\n")
        self.assertFalse(is_image_file(str(csv_path)))

    def test_upload_endpoint_success(self) -> None:
        """Test successful upload of valid image and document formats."""
        # JPEG Image Upload
        res = self.client.post(
            "/api/upload",
            data={"file": (BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01"), "temp_test_upload.jpg")}
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["type"], "image")
        self.assertEqual(data["context"], "The user uploaded an image.")

        # PDF Document Upload
        res = self.client.post(
            "/api/upload",
            data={"file": (BytesIO(b"%PDF-1.5\n%..."), "temp_test_upload.pdf")}
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["type"], "pdf")
        self.assertEqual(data["context"], "The user uploaded a document.")

        # CSV Spreadsheet Upload
        res = self.client.post(
            "/api/upload",
            data={"file": (BytesIO(b"crop,yield\nrice,50\n"), "temp_test_upload.csv")}
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["type"], "spreadsheet")
        self.assertEqual(data["context"], "The user uploaded tabular data.")

    def test_upload_endpoint_spoof_rejection(self) -> None:
        """Test that spoofed uploads (invalid file content for extension) are rejected."""
        # PDF disguised as JPG
        res = self.client.post(
            "/api/upload",
            data={"file": (BytesIO(b"%PDF-1.5\n%..."), "temp_test_spoof.jpg")}
        )
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn("error", data)
        self.assertIn("Spoofing detected", data["error"])

        # HTML disguised as PNG
        res = self.client.post(
            "/api/upload",
            data={"file": (BytesIO(b"<html><body>test</body></html>"), "temp_test_spoof.png")}
        )
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn("error", data)
        self.assertIn("Spoofing detected", data["error"])

    @patch("app.agents.coordinator_agent.call_weather_mcp_tool")
    @patch("app.agents.coordinator_agent.call_location_mcp_tool")
    @patch("app.agents.coordinator_agent.generate_execution_plan")
    @patch("app.agents.crop_agent.generate_text")
    @patch("app.services.response_generator.generate_text")
    def test_routing_for_pdf_file(self, mock_response_gen, mock_crop_text, mock_planner, mock_location, mock_weather) -> None:
        """Test that coordinator agent does NOT trigger disease routing for a PDF upload."""
        # Setup mocks
        mock_planner.return_value = {
            "steps": [{"step": 1, "agent": "crop", "action": "general advice"}],
            "required_data": [],
            "response_tone": "general"
        }
        mock_crop_text.return_value = "Mocked crop agent response"
        mock_response_gen.return_value = "Mocked response generator output"

        pdf_path = self.test_upload_dir / "temp_test_valid.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%...")

        # Process a general question with the PDF file path
        res = process_request(
            user_query="How should I grow mangoes?",
            image_path=str(pdf_path),
            latitude=None,
            longitude=None
        )

        # Assertions
        # 1. 'disease_agent' should NOT be used since it is a PDF document
        self.assertNotIn("disease_agent", res["agents_used"])
        # 2. 'crop_agent' should be used instead
        self.assertIn("crop_agent", res["agents_used"])


if __name__ == "__main__":
    unittest.main()
