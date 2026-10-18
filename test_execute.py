import httpx
import json

agent_id = "a2f51962-1754-4ff4-a5d3-0082625607cc"
url = f"https://agents-v2.dapta.ai/text-agent-v2/api/v2/agents/{agent_id}/execute"

# Let's test a message
payload = {
    "message": "Hola, somos Restaurante El Buen Sabor, categoría Restaurante. El perfil del cliente es la categoría del lead a calificar: Restaurante. Buscamos conseguir más comensales los fines de semana y llegamos por email.",
    "channel": "widget",
    "external_id": "test-lead-123"
}

r = httpx.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30.0)
print("Status code:", r.status_code)
try:
    data = r.json()
    with open("test_execute_resp.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Response JSON keys:", list(data.keys()))
    print("Conversation ID:", data.get("conversation_id"))
    print("Output:", data.get("output"))
    print("Status:", data.get("status"))
except Exception as e:
    print("Error:", e)
    print("Raw text:", r.text)
