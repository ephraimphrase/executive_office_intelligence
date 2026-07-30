import logging
import time
from datetime import datetime, timezone

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class MicrosoftGraphClient:
    def __init__(self):
        settings = get_settings()
        self.tenant_id = settings.azure_tenant_id
        self.client_id = settings.azure_client_id
        self.client_secret = settings.azure_client_secret
        self.graph_endpoint = settings.ms_graph_endpoint.rstrip("/")
        self.enabled = bool(self.tenant_id and self.client_id and self.client_secret)
        self._access_token = None
        self._token_expires_at = 0

    async def get_access_token(self) -> str:
        if not self.enabled:
            return "mock-token"

        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "scope": "https://graph.microsoft.com/.default",
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=data)
                response.raise_for_status()
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                self._token_expires_at = time.time() + token_data.get("expires_in", 3600) - 60
                return self._access_token
            except Exception as e:
                logger.error(f"Failed to get MS Graph token: {e}")
                return ""

    async def _headers(self) -> dict:
        token = await self.get_access_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response | None:
        url = f"{self.graph_endpoint}{path}"
        headers = await self._headers()
        headers.update(kwargs.pop("headers", {}) or {})
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response
        except Exception as e:
            logger.error(f"MS Graph {method} {path} failed: {e}")
            return None

    async def get_emails(self, user_email: str, since_datetime: str | None, limit: int = 50) -> list[dict]:
        if not self.enabled:
            return [
                {
                    "id": "mock-email-1",
                    "subject": "URGENT: Project Alpha Review",
                    "bodyPreview": "Please review the attached documents for the board meeting.",
                    "body": {"content": "Dear GVP,\n\nPlease review the attached documents for tomorrow's board meeting regarding Project Alpha. We need your approval on the budget allocation.\n\nThanks,\nJohn"},
                    "sender": {"emailAddress": {"address": "john.doe@dangote.com", "name": "John Doe"}},
                    "receivedDateTime": datetime.now(timezone.utc).isoformat() + "Z",
                    "hasAttachments": True
                },
                {
                    "id": "mock-email-2",
                    "subject": "Weekly Update: Dangote Cement",
                    "bodyPreview": "Production numbers are up by 5% this week.",
                    "body": {"content": "Production numbers are up by 5% this week. We met all our targets."},
                    "sender": {"emailAddress": {"address": "operations@dangote.com", "name": "Operations Team"}},
                    "receivedDateTime": datetime.now(timezone.utc).isoformat() + "Z",
                    "hasAttachments": False
                }
            ]

        params = {"$top": limit, "$orderby": "receivedDateTime desc"}
        if since_datetime:
            params["$filter"] = f"receivedDateTime ge {since_datetime}"
        response = await self._request("GET", f"/users/{user_email}/messages", params=params)
        return response.json().get("value", []) if response else []

    async def get_email_by_id(self, message_id: str, user_email: str | None = None) -> dict:
        if not self.enabled:
            return {"id": message_id, "subject": "Mock Subject", "body": {"content": "Mock Body"}}
        user_email = user_email or get_settings().gvp_email
        response = await self._request("GET", f"/users/{user_email}/messages/{message_id}")
        return response.json() if response else {}

    async def get_email_attachments(self, message_id: str, user_email: str | None = None) -> list[dict]:
        if not self.enabled:
            return [{"id": "attach-1", "name": "document.pdf", "contentType": "application/pdf", "contentBytes": "bW9jaw=="}]
        user_email = user_email or get_settings().gvp_email
        response = await self._request("GET", f"/users/{user_email}/messages/{message_id}/attachments")
        return response.json().get("value", []) if response else []

    async def send_email(self, to: str, subject: str, body: str, user_email: str | None = None) -> bool:
        if not self.enabled:
            logger.info(f"Mock sending email to {to}: {subject}")
            return True
        user_email = user_email or get_settings().gvp_email
        payload = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": to}}],
            },
            "saveToSentItems": True,
        }
        response = await self._request("POST", f"/users/{user_email}/sendMail", json=payload)
        return response is not None

    async def get_calendar_events(self, user_email: str, start_dt: str, end_dt: str) -> list[dict]:
        if not self.enabled:
            return [
                {
                    "id": "mock-event-1",
                    "subject": "Board Meeting",
                    "start": {"dateTime": start_dt, "timeZone": "UTC"},
                    "end": {"dateTime": start_dt, "timeZone": "UTC"},
                    "location": {"displayName": "Boardroom A"}
                }
            ]
        params = {"startDateTime": start_dt, "endDateTime": end_dt, "$orderby": "start/dateTime"}
        response = await self._request("GET", f"/users/{user_email}/calendarView", params=params)
        return response.json().get("value", []) if response else []

    async def create_calendar_event(self, user_email: str, event_data: dict) -> dict:
        if not self.enabled:
            event_data["id"] = "mock-new-event"
            return event_data
        response = await self._request("POST", f"/users/{user_email}/events", json=event_data)
        return response.json() if response else {}

    async def update_calendar_event(self, user_email: str, event_id: str, event_data: dict) -> dict:
        if not self.enabled:
            return event_data
        response = await self._request("PATCH", f"/users/{user_email}/events/{event_id}", json=event_data)
        return response.json() if response else {}

    async def delete_calendar_event(self, user_email: str, event_id: str) -> bool:
        if not self.enabled:
            return True
        response = await self._request("DELETE", f"/users/{user_email}/events/{event_id}")
        return response is not None

    async def list_drive_items(self, user_email: str, folder_path: str) -> list[dict]:
        if not self.enabled:
            return [{"id": "mock-file-1", "name": "Financial_Report.docx", "file": {"mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}}]
        path = "/drive/root/children" if not folder_path or folder_path == "/" else f"/drive/root:{folder_path}:/children"
        response = await self._request("GET", f"/users/{user_email}{path}")
        return response.json().get("value", []) if response else []

    async def download_file(self, user_email: str, item_id: str) -> bytes:
        if not self.enabled:
            return b"mock file content"
        response = await self._request("GET", f"/users/{user_email}/drive/items/{item_id}/content")
        return response.content if response else b""

    async def get_file_metadata(self, user_email: str, item_id: str) -> dict:
        if not self.enabled:
            return {"id": item_id, "name": "mock_file.pdf"}
        response = await self._request("GET", f"/users/{user_email}/drive/items/{item_id}")
        return response.json() if response else {}

    async def list_chats(self, user_email: str) -> list[dict]:
        """List the user's 1:1 and group Teams chats.
        Requires the Chat.Read (delegated) or Chat.Read.All (application)
        Graph permission with admin consent in the tenant."""
        if not self.enabled:
            return [{"id": "mock-chat-1", "topic": None, "chatType": "oneOnOne"}]
        response = await self._request("GET", f"/users/{user_email}/chats")
        return response.json().get("value", []) if response else []

    async def get_chat_messages(self, user_email: str, chat_id: str) -> list[dict]:
        if not self.enabled:
            return [{
                "id": "mock-teams-msg-1",
                "createdDateTime": datetime.now(timezone.utc).isoformat() + "Z",
                "from": {"user": {"displayName": "Chief of Staff", "id": "mock-user-id"}},
                "body": {"content": "Please schedule a follow-up on the Obajana site visit for Thursday."},
            }]
        params = {"$top": 50, "$orderby": "createdDateTime desc"}
        response = await self._request("GET", f"/users/{user_email}/chats/{chat_id}/messages", params=params)
        return response.json().get("value", []) if response else []

    async def list_joined_teams(self, user_email: str) -> list[dict]:
        if not self.enabled:
            return [{"id": "mock-team-1", "displayName": "Executive Office"}]
        response = await self._request("GET", f"/users/{user_email}/joinedTeams")
        return response.json().get("value", []) if response else []

    async def get_channel_messages(self, team_id: str, channel_id: str) -> list[dict]:
        if not self.enabled:
            return []
        response = await self._request("GET", f"/teams/{team_id}/channels/{channel_id}/messages")
        return response.json().get("value", []) if response else []
