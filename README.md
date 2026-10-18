# Motor de Leads — Demo en Render

## Publicar con Render

1. Sube este repositorio a GitHub.
2. En Render, selecciona **New + → Blueprint** y conecta el repositorio.
3. Render detectará `render.yaml` y propondrá crear el frontend y el backend.
4. Confirma el despliegue. Render asignará las URLs, las conectará mediante
   variables de entorno y desplegará ambos servicios.
5. Abre la URL pública del servicio `motor-leads-web`.

El frontend Next.js y la API FastAPI son servicios web independientes. El
Blueprint configura `NEXT_PUBLIC_API_URL`, `FRONTEND_URL`, CORS, el puerto
dinámico `PORT` de Render y los comandos de build y arranque.

## Alcance y límites de la demo

- Ambos servicios usan el plan gratuito definido en `render.yaml`. Pueden
  tardar en responder tras un período sin actividad.
- La base SQLite se guarda en `/tmp/motor_leads.db`, que es temporal. Los leads
  y cambios de la demo pueden perderse cuando Render reinicie o vuelva a
  desplegar el backend. No uses datos personales o sensibles.
- El scraper usa datos de muestra y los envíos de email, WhatsApp y formularios
  están simulados; no contactan negocios reales.
- La calificación solicita resultados al agente Dapta configurado en el
  backend. Su disponibilidad y límites dependen de esa cuenta/servicio.
- La API no tiene autenticación: cualquiera que conozca su URL puede invocar
  sus endpoints, incluidas acciones que modifican los datos de la demo. No la
  uses para información sensible ni para operaciones reales.

Si necesitas conservar datos, configura almacenamiento persistente compatible
con el plan de Render elegido o implementa una integración PostgreSQL antes de
usar la aplicación fuera de una demo temporal. El backend actual usa `sqlite3`:
cambiar `RUTA_BASE_DATOS` por una URL PostgreSQL no basta para migrarlo.

## Ejecución local

Backend, desde la raíz:

```powershell
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Frontend, en otra terminal:

```powershell
cd frontend
npm ci
npm run dev
```

El frontend usa `http://127.0.0.1:8000` como API local predeterminada. Para
apuntar a otro backend, define `NEXT_PUBLIC_API_URL` antes de iniciar o compilar
el frontend.
