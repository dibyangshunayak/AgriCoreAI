import sys
import json
sys.path.insert(0, '.')

from app.main import app

def test_chat_endpoint():
    print("Testing /api/chat endpoint...")
    client = app.test_client()
    payload = {
        "message": "Hello AgriCore AI",
        "latitude": 20.2961,
        "longitude": 85.8245,
        "history": [],
        "session_id": "test_session_123",
        "preferred_language": "en"
    }
    response = client.post(
        "/api/chat",
        data=json.dumps(payload),
        content_type="application/json"
    )
    print("Status Code:", response.status_code)
    print("Content Type:", response.content_type)
    
    # Read the streamed chunks
    print("Chunks received:")
    for chunk in response.response:
        print(chunk.decode('utf-8'))

if __name__ == "__main__":
    test_chat_endpoint()
