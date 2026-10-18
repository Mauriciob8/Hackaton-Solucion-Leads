from pathlib import Path
import httpx
import json

carpeta_datos = Path(__file__).resolve().parent / "data"

with open(carpeta_datos / "test_execute_resp.json", "r", encoding="utf-8") as f:
    prev = json.load(f)

conv_id = prev.get("conversation_id")
agent_id = "a2f51962-1754-4ff4-a5d3-0082625607cc"
url = f"https://agents-v2.dapta.ai/text-agent-v2/api/v2/agents/{agent_id}/execute"

payload = {
    "message": "Nivel alto en Instagram y Facebook.",
    "channel": "widget",
    "conversation_id": conv_id,
    "external_id": "test-lead-123"
}

r = httpx.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30.0)
data = r.json()
with open(carpeta_datos / "test_execute_resp2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Response 2 output:")
print(data.get("output"))
