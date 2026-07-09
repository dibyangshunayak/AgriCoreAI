import requests
import json

api_key = "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"
url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "nvidia/nemotron-3-nano-30b-a3b",
    "messages": [
        {"role": "user", "content": "Hi"}
    ],
    "temperature": 1,
    "top_p": 1,
    "max_tokens": 1024,
    "reasoning_budget": 1024,
    "stream": True
}

print("Testing streaming payload...")
response = requests.post(url, json=payload, headers=headers, stream=True)
print("Status Code:", response.status_code)

for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8').strip()
        if decoded_line.startswith("data: "):
            data_str = decoded_line[6:]
            if data_str == "[DONE]":
                print("\nStream Finished")
                break
            try:
                chunk = json.loads(data_str)
                # Print only the delta dictionary to see its keys
                delta = chunk["choices"][0]["delta"]
                print(json.dumps(delta, ensure_ascii=True))
            except Exception as e:
                print("Error parsing chunk:", e)
