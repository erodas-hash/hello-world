"""
Integracion con HubSpot para registrar leads generados por el agente de ventas.

Requiere una "Private App" de HubSpot con el scope `crm.objects.contacts.write`.
Genera el token en HubSpot: Configuracion -> Integraciones -> Private Apps.

Variable de entorno requerida:
    export HUBSPOT_ACCESS_TOKEN="pat-..."
"""

import os

import requests

HUBSPOT_API_BASE = "https://api.hubapi.com"


def register_lead(
    email: str,
    nombre: str | None = None,
    telefono: str | None = None,
    empresa: str | None = None,
    notas: str | None = None,
) -> str:
    """Crea o actualiza un contacto en HubSpot con la informacion del lead.

    Devuelve un mensaje corto que el agente puede usar como resultado de la
    herramienta (tool_result).
    """
    token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
    if not token:
        return "No se pudo registrar el lead: falta configurar HUBSPOT_ACCESS_TOKEN."

    properties = {"email": email}
    if nombre:
        partes = nombre.split(" ", 1)
        properties["firstname"] = partes[0]
        if len(partes) > 1:
            properties["lastname"] = partes[1]
    if telefono:
        properties["phone"] = telefono
    if empresa:
        properties["company"] = empresa
    if notas:
        properties["hs_lead_status"] = "NEW"
        properties["message"] = notas

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    create_resp = requests.post(
        f"{HUBSPOT_API_BASE}/crm/v3/objects/contacts",
        headers=headers,
        json={"properties": properties},
        timeout=10,
    )

    if create_resp.status_code in (200, 201):
        return f"Lead registrado en HubSpot correctamente ({email})."

    if create_resp.status_code == 409:
        # El contacto ya existe: actualizarlo en su lugar.
        search_resp = requests.post(
            f"{HUBSPOT_API_BASE}/crm/v3/objects/contacts/search",
            headers=headers,
            json={
                "filterGroups": [
                    {"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}
                ]
            },
            timeout=10,
        )
        search_resp.raise_for_status()
        results = search_resp.json().get("results", [])
        if not results:
            return f"No se pudo registrar ni actualizar el lead ({email})."

        contact_id = results[0]["id"]
        update_resp = requests.patch(
            f"{HUBSPOT_API_BASE}/crm/v3/objects/contacts/{contact_id}",
            headers=headers,
            json={"properties": properties},
            timeout=10,
        )
        if update_resp.status_code == 200:
            return f"Lead existente actualizado en HubSpot ({email})."
        return f"No se pudo actualizar el lead en HubSpot ({email}): {update_resp.text}"

    return f"No se pudo registrar el lead en HubSpot ({email}): {create_resp.text}"
