import httpx
import json

agent_id = "a2f51962-1754-4ff4-a5d3-0082625607cc"
url = f"https://agents-v2.dapta.ai/text-agent-v2/api/v2/agents/{agent_id}/execute"

# Test 1: Lead with category, need, social engagement, and channel
msg_qualified = (
    "Hola Leo, soy de Clínica Dental Sonrisas, categoría: Salud / Odontología. "
    "El perfil del cliente es la categoría del lead a calificar: Salud / Odontología. "
    "Nuestro principal problema es conseguir nuevos pacientes para ortodoncia. "
    "Tenemos interacción alta en redes sociales (Instagram y Facebook), "
    "y los contactamos por WhatsApp. "
    "Por favor califícanos."
)

r1 = httpx.post(url, json={"message": msg_qualified, "channel": "widget", "external_id": "test-dental-1"}, timeout=30.0)
print("Qualified response:")
data1 = r1.json()
with open("resp_dental.json", "w", encoding="utf-8") as f:
    json.dump(data1, f, indent=2, ensure_ascii=False)
print("Dental output:", data1.get("output"))

# Test 2: Lead that does not qualify due to low social engagement
msg_unqualified = (
    "Hola, somos Taller Mecánico Rapifix, categoría: Mecánica Automotriz. "
    "El perfil del cliente es la categoría del lead a calificar: Mecánica Automotriz. "
    "No tenemos redes sociales ni interactuamos en internet, "
    "Llegamos por email. ¿Podemos calificar?"
)
r2 = httpx.post(url, json={"message": msg_unqualified, "channel": "widget", "external_id": "test-taller-2"}, timeout=30.0)
print("\nUnqualified response:")
data2 = r2.json()
with open("resp_taller.json", "w", encoding="utf-8") as f:
    json.dump(data2, f, indent=2, ensure_ascii=False)
print("Taller output:", data2.get("output"))
