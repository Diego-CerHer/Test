import requests
import config

BASE_URL = f"https://graph.facebook.com/v18.0/{config.PHONE_NUMBER_ID}"
HEADERS = {
    "Content-Type": "application/json",
}


def _headers():
    return {**HEADERS, "Authorization": f"Bearer {config.WHATSAPP_TOKEN}"}


def send_text(to: str, message: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    r = requests.post(f"{BASE_URL}/messages", json=payload, headers=_headers())
    r.raise_for_status()


def send_buttons(to: str, body: str, opciones: list[dict]):
    """
    opciones = [{"id": "ALTO", "title": "Alto"}, ...]
    Máximo 3 botones por limitación de WhatsApp
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": op["id"], "title": op["title"]}}
                    for op in opciones
                ]
            }
        }
    }
    r = requests.post(f"{BASE_URL}/messages", json=payload, headers=_headers())
    r.raise_for_status()
