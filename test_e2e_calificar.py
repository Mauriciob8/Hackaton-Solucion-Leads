import httpx
import json

# 1. Obtener leads
r = httpx.get("http://127.0.0.1:8000/api/leads?tamano=10")
data = r.json()
leads = data.get("leads", [])
print(f"Total leads: {len(leads)}")

lead_to_test = None
for l in leads:
    print(f"- [{l['id'][:8]}] {l['nombre_negocio']} | Categoria: {l['sector']} | Estado: {l['estado']}")
    if l['estado'] == 'respondio' and not lead_to_test:
        lead_to_test = l

# Si no hay uno en 'respondio', busquemos uno en 'contactado' o 'detectado' y avancémoslo
if not lead_to_test and leads:
    cand = leads[0]
    lead_id = cand['id']
    print(f"\nAvanzando lead {cand['nombre_negocio']} a 'respondio'...")
    if cand['estado'] == 'detectado':
        httpx.post(f"http://127.0.0.1:8000/api/leads/{lead_id}/contactar")
    httpx.post(f"http://127.0.0.1:8000/api/leads/{lead_id}/respuesta", json={"lead_id": lead_id, "opcion": "A"})
    lead_to_test = httpx.get(f"http://127.0.0.1:8000/api/leads/{lead_id}").json()

if lead_to_test:
    lead_id = lead_to_test['id']
    print(f"\nProbando calificación con Agente Dapta para lead: {lead_to_test['nombre_negocio']} (Categoría: {lead_to_test['sector']})...")
    res_cal = httpx.post(f"http://127.0.0.1:8000/api/leads/{lead_id}/calificar", timeout=35.0)
    print("Status code:", res_cal.status_code)
    cal_data = res_cal.json()
    with open("cal_result.json", "w", encoding="utf-8") as f:
        json.dump(cal_data, f, indent=2, ensure_ascii=False)
    print("Respuesta de calificación guardada en cal_result.json:")
    print("Nuevo estado de la empresa:", cal_data.get("nuevo_estado"))
    print("Categoría enviada:", cal_data.get("categoria"))
    print("Feedback Dapta:", cal_data.get("feedback_dapta"))
else:
    print("No se encontraron leads para probar.")
