"""
Agente de IA de ventas basado en Claude (Anthropic API).

Uso:
    export ANTHROPIC_API_KEY="tu-api-key"
    python sales_agent.py

El agente actua como un asistente de ventas que conoce el catalogo
definido en `catalog.json`, responde preguntas de clientes, recomienda
productos y trata de avanzar la conversacion hacia una venta.
"""

import json
import os
import sys

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


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: define la variable de entorno ANTHROPIC_API_KEY", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    catalog = load_catalog()
    system_prompt = build_system_prompt(catalog)

    messages: list[dict] = []

    print("Agente de ventas listo. Escribe 'salir' para terminar.\n")

    while True:
        user_input = input("Tu: ").strip()
        if user_input.lower() in {"salir", "exit", "quit"}:
            print("Agente: ¡Gracias por tu visita! Hasta luego.")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )

        reply = "".join(
            block.text for block in response.content if block.type == "text"
        )
        print(f"Agente: {reply}\n")

        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
