import httpx
import json

agent_id = "a2f51962-1754-4ff4-a5d3-0082625607cc"

url1 = f"https://api.dapta.ai/api/8f5211b70a46e83b/get_agent_id_by_id?x-api-key=vDEGq-8f5211b7-ea23-4f31-b0ab-29710a46e83b-a&id={agent_id}"
r1 = httpx.get(url1)
print("r1 status:", r1.status_code)
print("r1 body:", r1.text)

try:
    res = r1.json()
    resolved_id = res.get("agent_id", agent_id)
except Exception:
    resolved_id = agent_id

url2 = f"https://agents-v2.dapta.ai/text-agent-v2/api/v2/agents/{resolved_id}"
r2 = httpx.get(url2, headers={
    "x-api-key": "kn6hP-8f5211b7-ea23-4f31-b0ab-29710a46e83b-f",
    "Content-Type": "application/json"
})
print("r2 status:", r2.status_code)
try:
    data = r2.json()
    print("agent name:", data.get("name"))
    print("description:", data.get("description"))
    print("system prompt snippet:", (data.get("system_prompt") or data.get("prompt") or "")[:400])
    print("keys in agent data:", list(data.keys()))
except Exception as e:
    print("Error parsing r2:", e)
    print("r2 text:", r2.text[:500])
