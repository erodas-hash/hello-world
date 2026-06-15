"""
Integracion del agente de IA de ventas con Slack (modo Socket).

Requisitos previos en Slack:
1. Crea una app en https://api.slack.com/apps.
2. Activa "Socket Mode" y genera un App-Level Token con el scope
   `connections:write` (empieza con "xapp-").
3. En "OAuth & Permissions" agrega los scopes de Bot Token:
   - app_mentions:read
   - chat:write
   - im:history
   - im:read
   - im:write
4. Suscribe los eventos del bot ("Event Subscriptions" -> Subscribe to
   bot events): `message.im` y `app_mention`.
5. Instala la app en tu workspace y copia el Bot User OAuth Token
   (empieza con "xoxb-").

Variables de entorno requeridas:
    export ANTHROPIC_API_KEY="tu-api-key-de-anthropic"
    export SLACK_BOT_TOKEN="xoxb-..."
    export SLACK_APP_TOKEN="xapp-..."

Uso:
    pip install -r requirements.txt
    python slack_agent.py

El bot responde a mensajes directos (DM) y a menciones (@bot) en canales,
manteniendo el historial de conversacion por canal/usuario usando el
mismo agente de ventas que la version CLI.
"""

import os
import sys

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from sales_agent_core import SalesAgent


def main() -> None:
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_app_token = os.environ.get("SLACK_APP_TOKEN")

    missing = [
        name
        for name, value in [
            ("ANTHROPIC_API_KEY", anthropic_key),
            ("SLACK_BOT_TOKEN", slack_bot_token),
            ("SLACK_APP_TOKEN", slack_app_token),
        ]
        if not value
    ]
    if missing:
        print(f"Error: define las variables de entorno: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    agent = SalesAgent(api_key=anthropic_key)
    app = App(token=slack_bot_token)

    @app.event("message")
    def handle_dm(event, say):
        # Solo responder a mensajes directos de usuarios (ignorar bots/ediciones).
        if event.get("channel_type") != "im" or event.get("bot_id"):
            return
        user_text = event.get("text", "").strip()
        if not user_text:
            return
        session_id = event["channel"]
        reply = agent.reply(session_id=session_id, user_text=user_text)
        say(text=reply)

    @app.event("app_mention")
    def handle_mention(event, say):
        user_text = event.get("text", "").strip()
        if not user_text:
            return
        session_id = event["channel"]
        reply = agent.reply(session_id=session_id, user_text=user_text)
        say(text=reply, thread_ts=event.get("ts"))

    print("Agente de ventas conectado a Slack (Socket Mode). Esperando mensajes...")
    SocketModeHandler(app, slack_app_token).start()


if __name__ == "__main__":
    main()
