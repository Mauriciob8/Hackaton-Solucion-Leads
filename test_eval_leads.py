import httpx
import json

agent_id = "a2f51962-1754-4ff4-a5d3-0082625607cc"
url = f"https://agents-v2.dapta.ai/text-agent-v2/api/v2/agents/{agent_id}/execute"

leads_test = [
    {
        "nombre": "Restaurante La Casona",
        "categoria": "Gastronomía / Restaurante",
        "canal": "whatsapp",
        "necesidad": "Aumentar reservaciones de mesa los fines de semana",
        "redes": "Interacción alta en Instagram y TikTok",
        "ingresos": "Ingresos mensuales superiores a 500 USD (aprox 3500 USD)",
    },
    {
        "nombre": "Boutique Sofía",
        "categoria": "Moda y Calzado",
        "canal": "email",
        "necesidad": "Liquidación de inventario de temporada",
        "redes": "Nivel medio en Facebook",
        "ingresos": "Ingresos mensuales de 200 USD (menor a 500 USD)",
    },
    {
        "nombre": "Ferretería Central",
        "categoria": "Ferretería y Construcción",
        "canal": "formulario_web",
        "necesidad": "Vender por internet",
        "redes": "Sin redes sociales activas",
        "ingresos": "Ingreso no especificado aún",
    }
]

for idx, l in enumerate(leads_test):
    msg = (
        f"Hola Leo, tengo la información completa para calificar este lead de HackatonPrueba:\n"
        f"- Empresa: {l['nombre']}\n"
        f"- Categoría: {l['categoria']}\n"
        f"- Canal de contacto: {l['canal']}\n"
        f"- Necesidad principal: {l['necesidad']}\n"
        f"- Nivel de interacción en redes: {l['redes']}\n"
        f"- Ingreso mensual / esfuerzos: {l['ingresos']}\n\n"
        f"Con estos 4 criterios, por favor clasifica a {l['nombre']} indicando claramente si queda Calificado, En revisión o No calificado."
    )
    r = httpx.post(url, json={"message": msg, "channel": "widget", "external_id": f"test-lead-{idx}"}, timeout=30.0)
    data = r.json()
    print(f"=== RESULTADO LEAD {idx+1}: {l['nombre']} ({l['categoria']}) ===")
    out = data.get("output", "")
    print(out)
    print("Tool calls:", data.get("tool_calls"))
    print()
