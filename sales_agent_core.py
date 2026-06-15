"""
Logica compartida del agente de IA de ventas (Anthropic / Claude).

Este modulo se reutiliza tanto desde la CLI (`sales_agent.py`) como desde
la integracion con Slack (`slack_agent.py`).
"""

import json
import os

import anthropic

from hubspot_integration import register_lead

MODEL = "claude-sonnet-4-6"
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "catalog.json")

REGISTER_LEAD_TOOL = {
    "name": "register_lead",
    "description": (
        "Registra o actualiza un lead en HubSpot. Usa esta herramienta solo "
        "cuando el cliente haya proporcionado al menos su email y muestre "
        "interes real en algun producto."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "Correo del cliente"},
            "nombre": {"type": "string", "description": "Nombre completo del cliente"},
            "telefono": {"type": "string", "description": "Telefono de contacto"},
            "empresa": {"type": "string", "description": "Empresa del cliente"},
            "notas": {
                "type": "string",
                "description": "Resumen de la necesidad/interes del cliente para el equipo de ventas",
            },
        },
        "required": ["email"],
    },
}


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
- Cuando el cliente comparta su email y muestre interes real en un producto,
  usa la herramienta `register_lead` para guardarlo en HubSpot antes de
  continuar la conversacion.

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

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=self.system_prompt,
                messages=messages,
                tools=[REGISTER_LEAD_TOOL],
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                return "".join(
                    block.text for block in response.content if block.type == "text"
                )

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if block.name == "register_lead":
                    result_text = register_lead(**block.input)
                else:
                    result_text = f"Herramienta desconocida: {block.name}"
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    }
                )

            messages.append({"role": "user", "content": tool_results})
