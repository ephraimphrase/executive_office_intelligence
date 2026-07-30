import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

class WhatsAppClient:
    def __init__(self):
        settings = get_settings()
        self.token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.verify_token = settings.whatsapp_verify_token or "eois-verify-token"
        self.api_version = settings.whatsapp_api_version
        self.use_mock = not bool(self.token and self.phone_number_id)
        
        if self.use_mock:
            logger.info("WhatsApp credentials not set, using mock mode.")

    async def send_message(self, phone_number: str, text: str) -> bool:
        if self.use_mock:
            logger.info(f"MOCK WhatsApp to {phone_number}: {text}")
            return True
            
        url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": text}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            return response.status_code == 200

    async def send_template_message(self, phone_number: str, template_name: str, params: list) -> bool:
        if self.use_mock:
            logger.info(f"MOCK WhatsApp Template '{template_name}' to {phone_number} with params {params}")
            return True
        return True

    def parse_webhook_message(self, payload: dict) -> dict:
        try:
            entry = payload["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            messages = value.get("messages", [])
            
            if not messages:
                return {}
                
            msg = messages[0]
            return {
                "id": msg.get("id"),
                "from_number": msg.get("from"),
                "timestamp": msg.get("timestamp"),
                "message_type": msg.get("type"),
                "text": msg.get("text", {}).get("body") if msg.get("type") == "text" else None,
                "media_url": None
            }
        except (KeyError, IndexError):
            return {}

    def verify_webhook(self, token: str, challenge: str) -> str:
        if token == self.verify_token:
            return challenge
        return ""
