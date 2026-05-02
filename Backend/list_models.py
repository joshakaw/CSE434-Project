"""Run this to see which Gemini models your API key can access."""
import json, requests

with open('secrets.json') as f:
    key = json.load(f)['gemini_api_key']

url = "https://generativelanguage.googleapis.com/v1beta/models?key={}".format(key)
resp = requests.get(url)
print("Status:", resp.status_code)
if resp.ok:
    for m in resp.json().get("models", []):
        name = m.get("name", "")
        methods = m.get("supportedGenerationMethods", [])
        if "generateContent" in methods:
            print(" ", name)
else:
    print(resp.text)
