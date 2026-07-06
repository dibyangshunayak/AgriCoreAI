import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.agents.coordinator_agent import process_request

def create_temp_image(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (300, 300), color=(34, 139, 34))
    draw = ImageDraw.Draw(img)
    draw.ellipse([100, 100, 200, 200], fill=(218, 165, 32))
    img.save(path, "JPEG")

def safe_print(label: str, val) -> None:
    try:
        print(f"{label} {val}")
    except UnicodeEncodeError:
        try:
            escaped = str(val).encode('ascii', errors='backslashreplace').decode('ascii')
            print(f"{label} {escaped}")
        except Exception:
            print(f"{label} <encoding error>")

def run_test():
    print("AgriCore Manual Verification Suite")
    print("=" * 60)

    # 1. hello (greeting)
    print("\n[1] Query: 'hello'")
    res = process_request("hello")
    safe_print("Agents Used:", res.get('agents_used'))
    safe_print("Response:", res.get('recommendation'))

    # 2. who are you (greeting)
    print("\n[2] Query: 'who are you'")
    res = process_request("who are you")
    safe_print("Agents Used:", res.get('agents_used'))
    safe_print("Response:", res.get('recommendation'))

    # 3. how much watr paddy need (spelling correction + crop)
    print("\n[3] Query: 'how much watr paddy need'")
    res = process_request("how much watr paddy need")
    safe_print("Agents Used:", res.get('agents_used'))
    safe_print("Response:", res.get('recommendation'))

    # 4. rice cultevation (spelling correction + crop)
    print("\n[4] Query: 'rice cultevation'")
    res = process_request("rice cultevation")
    safe_print("Agents Used:", res.get('agents_used'))
    safe_print("Response:", res.get('recommendation'))

    # 5. wether tommorow (spelling correction + weather)
    print("\n[5] Query: 'wether tommorow'")
    res = process_request("wether tommorow", latitude=20.296, longitude=85.824)
    safe_print("Agents Used:", res.get('agents_used'))
    safe_print("Response:", res.get('recommendation'))

    # 6. tell me my location (location)
    print("\n[6] Query: 'tell me my location'")
    res = process_request("tell me my location", latitude=20.296, longitude=85.824)
    safe_print("Agents Used:", res.get('agents_used'))
    safe_print("Response:", res.get('recommendation'))

    # 7. my tomato leaves have brown spots (disease)
    safe_print("\n[7] Query:", "'my tomato leaves have brown spots'")
    img_path = BACKEND_DIR / "uploads" / "temp_tomato.jpg"
    create_temp_image(img_path)
    res = process_request("my tomato leaves have brown spots", image_path=str(img_path))
    if "error" in res:
        safe_print("Error:", res.get("error"))
        safe_print("Reason:", res.get("reason"))
    else:
        safe_print("Agents Used:", res.get('agents_used'))
        safe_print("Response:", res.get('recommendation'))
    if img_path.exists():
        img_path.unlink()

    # 8. should i irrigate my paddy tomorrow (crop + weather complex query)
    safe_print("\n[8] Query:", "'should i irrigate my paddy tomorrow'")
    res = process_request("should i irrigate my paddy tomorrow", latitude=20.296, longitude=85.824)
    safe_print("Agents Used:", res.get('agents_used'))
    safe_print("Response:", res.get('recommendation'))

    # 9. धान को कितना पानी चाहिए (Hindi crop query)
    safe_print("\n[9] Query:", "'धान को कितना पानी चाहिए'")
    res = process_request("धान को कितना पानी चाहिए")
    safe_print("Agents Used:", res.get('agents_used'))
    safe_print("Response:", res.get('recommendation'))

    # 10. ଧାନକୁ କେତେ ପାଣି ଦରକାର (Odia crop query)
    safe_print("\n[10] Query:", "'ଧାନକୁ କେତେ ପାଣି ଦରକାର'")
    res = process_request("ଧାନକୁ କେତେ ପାଣି ଦରକାର")
    safe_print("Agents Used:", res.get('agents_used'))
    safe_print("Response:", res.get('recommendation'))

    print("=" * 60)
    print("Verification completed successfully!")

if __name__ == "__main__":
    run_test()
