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
