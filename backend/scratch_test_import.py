import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.config import settings
from app.services.nvidia_service import generate_text

print("Settings NVIDIA_API_KEY:", settings.NVIDIA_API_KEY[:10] + "..." if settings.NVIDIA_API_KEY else "None")
print("Settings NVIDIA_MODEL:", settings.NVIDIA_MODEL)
print("Settings NVIDIA_API_URL:", settings.NVIDIA_API_URL)

try:
    res = generate_text("Tell me a one sentence agriculture tip.")
    print("Result:", json.dumps(res, ensure_ascii=True))
except Exception as e:
    print("Failed with exception:", e)
