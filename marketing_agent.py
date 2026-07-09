"""
Agente de IA de Marketing basado en el modelo AIDA (Anthropic / Claude).

Genera contenido de marketing estructurado en 4 etapas:
  A - Atencion  : capta la atencion del cliente
  I - Interes   : genera interes en el producto/servicio
  D - Deseo     : convierte el interes en deseo de compra
  A - Accion    : impulsa al cliente a actuar (comprar, contactar, registrarse)

Uso:
    export ANTHROPIC_API_KEY="tu-api-key"
    python marketing_agent.py
"""

import os
import sys

import anthropic

MODEL = "claude-sonnet-4-6"

CONTENT_TYPES = {
    "1": "Email de ventas",
    "2": "Post para redes sociales (LinkedIn)",
    "3": "Post para redes sociales (Instagram/Facebook)",
    "4": "Anuncio publicitario (Google Ads / texto corto)",
    "5": "Mensaje de WhatsApp",
    "6": "Guion de video corto (30-60 segundos)",
}

SYSTEM_PROMPT = """Eres un experto en marketing digital y copywriting especializado en el modelo AIDA.

El modelo AIDA estructura el contenido en 4 etapas:
- ATENCION: Un gancho poderoso que detiene al lector/espectador (titulo, primera linea, pregunta impactante).
- INTERES: Informacion relevante que conecta con el problema o necesidad del publico objetivo.
- DESEO: Beneficios concretos, prueba social, resultados reales que hacen que el cliente QUIERA el producto.
- ACCION: Un llamado a la accion (CTA) claro, urgente y especifico.

Cuando generes contenido:
1. Estructura claramente cada seccion con el label correspondiente (ATENCION, INTERES, DESEO, ACCION).
2. Adapta el tono y longitud al tipo de contenido solicitado.
3. Usa lenguaje persuasivo, claro y orientado al publico objetivo.
4. Incluye emojis si el formato lo permite (redes sociales, WhatsApp).
5. Al final, ofrece una variacion alternativa o consejo para mejorar el contenido.
"""


def get_user_input(prompt: str) -> str:
    value = input(prompt).strip()
    while not value:
        value = input(f"  (no puede estar vacio) {prompt}").strip()
    return value


def select_content_type() -> str:
    print("\nTipo de contenido a generar:")
    for key, label in CONTENT_TYPES.items():
        print(f"  {key}. {label}")
    choice = input("\nElige una opcion (1-6): ").strip()
    while choice not in CONTENT_TYPES:
        choice = input("  Opcion invalida. Elige entre 1 y 6: ").strip()
    return CONTENT_TYPES[choice]


def build_user_prompt(
    producto: str,
    publico: str,
    beneficio: str,
    cta: str,
    tipo: str,
    tono: str,
) -> str:
    return f"""Genera un {tipo} usando el modelo AIDA con la siguiente informacion:

Producto/Servicio: {producto}
Publico objetivo: {publico}
Principal beneficio o propuesta de valor: {beneficio}
Llamado a la accion deseado (CTA): {cta}
Tono de comunicacion: {tono}

Estructura el contenido claramente con las etapas ATENCION, INTERES, DESEO y ACCION.
"""


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: define la variable de entorno ANTHROPIC_API_KEY", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print("=" * 55)
    print("   AGENTE DE MARKETING IA — Modelo AIDA")
    print("=" * 55)

    while True:
        print("\n--- Nueva pieza de contenido ---")

        producto = get_user_input("Producto o servicio: ")
        publico = get_user_input("Publico objetivo (quien es tu cliente ideal): ")
        beneficio = get_user_input("Principal beneficio o propuesta de valor: ")
        cta = get_user_input("CTA deseado (ej: 'Agenda una demo', 'Compra ahora'): ")
        tono = input("Tono de comunicacion (ej: profesional, casual, urgente) [profesional]: ").strip() or "profesional"
        tipo = select_content_type()

        print(f"\nGenerando {tipo}...\n")

        user_prompt = build_user_prompt(producto, publico, beneficio, cta, tipo, tono)

        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = "".join(
            block.text for block in response.content if block.type == "text"
        )

        print("=" * 55)
        print(content)
        print("=" * 55)

        otra = input("\n¿Generar otro contenido? (s/n): ").strip().lower()
        if otra not in {"s", "si", "sí", "yes", "y"}:
            print("\n¡Hasta luego! Recuerda: Atencion → Interes → Deseo → Accion.")
            break


if __name__ == "__main__":
    main()
