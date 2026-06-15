# hello-world
Este repositorio es para practicar el flujo de GitHub

## Agente de IA de ventas

Este repo incluye un agente de ventas conversacional basado en la API de Claude (Anthropic).

### Requisitos

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="tu-api-key"
```

### Uso

```bash
python sales_agent.py
```

El agente conoce el catálogo de productos definido en `catalog.json` y conversa
con el cliente para entender sus necesidades, recomendar productos y avanzar
hacia el cierre de la venta. Puedes editar `catalog.json` para adaptarlo a tus
propios productos o servicios.

### Integración con Slack

El mismo agente puede conectarse a Slack mediante Socket Mode (no requiere
exponer un servidor público).

1. Crea una app en https://api.slack.com/apps.
2. Activa **Socket Mode** y genera un App-Level Token con el scope
   `connections:write` (empieza con `xapp-`).
3. En **OAuth & Permissions**, agrega estos scopes de Bot Token:
   - `app_mentions:read`
   - `chat:write`
   - `im:history`
   - `im:read`
   - `im:write`
4. En **Event Subscriptions**, suscribe los eventos del bot:
   `message.im` y `app_mention`.
5. Instala la app en tu workspace y copia el Bot User OAuth Token
   (empieza con `xoxb-`).

Luego configura las variables de entorno y ejecuta:

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="tu-api-key"
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
python slack_agent.py
```

El bot responderá a mensajes directos (DM) y a menciones (`@bot`) en canales,
manteniendo el historial de conversación por canal/usuario.

### Integración con HubSpot (captura de leads)

El agente puede registrar automáticamente los leads en HubSpot cuando el
cliente comparte su correo y muestra interés real en un producto.

1. En HubSpot ve a **Configuración → Integraciones → Private Apps** y crea
   una app con el scope `crm.objects.contacts.write`.
2. Copia el token generado (empieza con `pat-`).
3. Define la variable de entorno:

```bash
export HUBSPOT_ACCESS_TOKEN="pat-..."
```

Con esta variable configurada (tanto en `sales_agent.py` como en
`slack_agent.py`), el agente usa la herramienta `register_lead` para crear o
actualizar el contacto en HubSpot con su email, nombre, teléfono, empresa y
una nota con el resumen de su interés, sin intervención manual.

Si `HUBSPOT_ACCESS_TOKEN` no está definido, el agente sigue funcionando
normalmente, solo que no registrará los leads en HubSpot.
