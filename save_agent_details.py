import httpx
import json

url2 = "https://agents-v2.dapta.ai/text-agent-v2/api/v2/agents/a2f51962-1754-4ff4-a5d3-0082625607cc"
r2 = httpx.get(url2, headers={
    "x-api-key": "kn6hP-8f5211b7-ea23-4f31-b0ab-29710a46e83b-f",
    "Content-Type": "application/json"
})
data = r2.json()
with open("agent_details.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Saved agent_details.json")
print("Instructions:", data.get("instructions"))
print("Purpose:", data.get("purpose"))
print("Variables:", data.get("variables"))
print("Tools:", data.get("tools"))
