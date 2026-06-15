"""
Agente de IA de ventas basado en Claude (Anthropic API) - version CLI.

Uso:
    export ANTHROPIC_API_KEY="tu-api-key"
    python sales_agent.py

El agente actua como un asistente de ventas que conoce el catalogo
definido en `catalog.json`, responde preguntas de clientes, recomienda
productos y trata de avanzar la conversacion hacia una venta.
"""

import os
import sys

from sales_agent_core import SalesAgent


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: define la variable de entorno ANTHROPIC_API_KEY", file=sys.stderr)
        sys.exit(1)

    agent = SalesAgent(api_key=api_key)

    print("Agente de ventas listo. Escribe 'salir' para terminar.\n")

    while True:
        user_input = input("Tu: ").strip()
        if user_input.lower() in {"salir", "exit", "quit"}:
            print("Agente: ¡Gracias por tu visita! Hasta luego.")
            break
        if not user_input:
            continue

        reply = agent.reply(session_id="cli", user_text=user_input)
        print(f"Agente: {reply}\n")


if __name__ == "__main__":
    main()
