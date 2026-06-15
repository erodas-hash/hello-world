"""
Logica compartida del agente de IA de ventas (Anthropic / Claude).

Este modulo se reutiliza tanto desde la CLI (`sales_agent.py`) como desde
la integracion con Slack (`slack_agent.py`).
"""

import json
import os

import anthropic

MODEL = "claude-sonnet-4-6"
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "catalog.json")


def load_catalog() -> list[dict]:
    if not os.path.exists(CATALOG_PATH):
        return []
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt(catalog: list[dict]) -> str:
    catalog_text = json.dumps(catalog, ensure_ascii=False, indent=2)
    return f"""Eres un agente de ventas amable, profesional y proactivo.

Tu objetivo es:
- Entender las necesidades del cliente.
- Recomendar productos del catalogo que mejor se ajusten a esas necesidades.
- Responder dudas sobre precios, caracteristicas y disponibilidad.
- Guiar la conversacion hacia el cierre de la venta (siguiente paso: cotizacion, pedido o contacto con un humano).
- Si el cliente pide algo que no esta en el catalogo, sugiere alternativas similares.

Catalogo de productos disponible (formato JSON):
{catalog_text}

Reglas:
- No inventes productos ni precios que no existan en el catalogo.
- Se conciso, calido y orientado a resolver la necesidad del cliente.
- Si no tienes informacion suficiente, pide los detalles que necesites.
"""


class SalesAgent:
    """Agente de ventas con memoria de conversacion por sesion."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt = build_system_prompt(load_catalog())
        self._conversations: dict[str, list[dict]] = {}

    def reply(self, session_id: str, user_text: str) -> str:
        messages = self._conversations.setdefault(session_id, [])
        messages.append({"role": "user", "content": user_text})

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=self.system_prompt,
            messages=messages,
        )

        reply_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        messages.append({"role": "assistant", "content": reply_text})
        return reply_text
