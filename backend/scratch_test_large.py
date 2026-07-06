import requests
import json

api_key = "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"
url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Payload with original values of max_tokens and reasoning_budget in the root
payload = {
    "model": "nvidia/nemotron-3-nano-30b-a3b",
    "messages": [
        {"role": "user", "content": "Hello"}
    ],
    "temperature": 1,
    "top_p": 1,
    "max_tokens": 16384,
    "reasoning_budget": 16384,
    "stream": False
}

print("Testing large values...")
response = requests.post(url, json=payload, headers=headers)
print("Status Code:", response.status_code)
try:
    print("Response JSON:", json.dumps(response.json(), ensure_ascii=True))
except Exception as e:
    print("Failed to serialize or print:", e)
