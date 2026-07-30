import logging
from datetime import datetime, timezone

from agents.email_agent import EmailIntelligenceAgent
from app.integrations.openai_client import get_openai_client

logger = logging.getLogger(__name__)

# The AI extraction vocabulary (CRITICAL/HIGH/MEDIUM/LOW) doesn't line up 1:1
# with EmailPriority's stored values (URGENT/HIGH/NORMAL/LOW).
_PRIORITY_MAP = {"CRITICAL": "URGENT", "HIGH": "HIGH", "MEDIUM": "NORMAL", "LOW": "LOW"}


class EmailProcessorService:
    def __init__(self):
        self.agent = EmailIntelligenceAgent(get_openai_client())

    async def _analyze(self, subject: str, body: str, sender: str, received_at: str) -> dict:
        return await self.agent.analyze_email(
            subject=subject, body=body, sender=sender, received_at=received_at
        )

    def _apply_analysis(self, record, analysis: dict) -> None:
        from app.models.email_record import EmailStatus

        record.ai_summary = analysis.get("summary")
        record.ai_meeting_requests = analysis.get("meeting_requests", [])
        record.ai_reschedule_requests = analysis.get("reschedule_requests", [])
        record.ai_action_items = analysis.get("action_items", [])
        record.ai_decisions = analysis.get("decisions", [])
        record.ai_risks = analysis.get("risks", [])
        record.ai_commitments = analysis.get("commitments", [])
        record.suggested_reply = analysis.get("suggested_reply")

        priority = (analysis.get("priority_level") or "").upper()
        record.priority = _PRIORITY_MAP.get(priority, "NORMAL")
        record.is_high_priority = priority in ("CRITICAL", "HIGH")

        department = analysis.get("department")
        if department:
            record.department_category = department

        record.processed_at = datetime.now(timezone.utc)

        # "Archive Processed Emails" — only auto-transition the default state;
        # never clobber a status the user (or a reply flow) already set.
        if record.status == EmailStatus.UNREAD:
            record.status = EmailStatus.PROCESSED

    async def _process_attachments(self, record, message_id, db) -> None:
        """Download email attachments, extract their text, and index them as
        searchable Documents — the spec's 'Read Attachments' capability."""
        if not record.has_attachments or not message_id or db is None:
            return

        import base64

        from app.integrations.microsoft_graph import MicrosoftGraphClient
        from app.models.document import Document
        from app.services.knowledge_base import KnowledgeBaseService

        graph = MicrosoftGraphClient()
        kb = KnowledgeBaseService()

        try:
            attachments = await graph.get_email_attachments(message_id)
        except Exception as e:
            logger.warning(f"Failed to fetch attachments for {message_id}: {e}")
            return

        names = []
        for att in attachments:
            name = att.get("name") or "attachment"
            names.append(name)
            content_b64 = att.get("contentBytes")
            if not content_b64:
                continue
            try:
                file_bytes = base64.b64decode(content_b64)
            except Exception:
                continue

            file_type = kb._infer_file_type(name, att.get("contentType", ""))
            text = await kb.extract_text_from_file(file_bytes, file_type)

            doc = Document(
                name=name,
                file_type=file_type,
                department=record.department_category,
                category="EMAIL_ATTACHMENT",
                ai_summary=text[:500] if text else None,
            )
            db.add(doc)
            await db.flush()
            await kb.index_document(str(doc.id), name, text, file_type, {}, db)

        if names:
            record.attachment_names = names
            await db.commit()

    async def _notify_if_high_priority(self, record, db) -> None:
        if not record.is_high_priority or db is None:
            return

        from app.models.notification import NotificationPriority, NotificationType
        from app.services.calendar_service import get_gvp_owner_id
        from app.services.notification_service import NotificationService

        owner_id = await get_gvp_owner_id(db)
        if owner_id is None:
            return

        await NotificationService().create_notification(
            user_id=owner_id,
            type=NotificationType.CRITICAL_EMAIL,
            title=f"High-priority email: {record.subject or '(no subject)'}",
            message=record.ai_summary or record.body_preview or "",
            priority=NotificationPriority.URGENT,
            reference_type="EMAIL",
            reference_id=record.id,
            db=db,
        )

    async def _run_extraction_pipeline(self, record, db, auto_create: bool) -> None:
        """Shared tail end of processing: notifications, then auto-create
        events/tasks/decisions/commitments/risks, then apply reschedules."""
        from app.services.calendar_service import get_gvp_owner_id
        from app.services.extraction_pipeline import apply_reschedules, auto_create_records

        await self._notify_if_high_priority(record, db)

        owner_id = await get_gvp_owner_id(db)
        extracted = {
            "meeting_requests": record.ai_meeting_requests,
            "action_items": record.ai_action_items,
            "decisions": record.ai_decisions,
            "commitments": record.ai_commitments,
            "risks": record.ai_risks,
            "department": record.department_category,
        }
        if auto_create:
            await auto_create_records("EMAIL", str(record.id), extracted, owner_id, db)
        await apply_reschedules(record.ai_reschedule_requests, owner_id, db)

    async def process_and_store(self, email_data: dict, db):
        """Analyze a raw Microsoft Graph email payload and persist it as a new EmailRecord."""
        from dateutil import parser as date_parser

        from app.models.email_record import EmailRecord

        subject = email_data.get("subject", "")
        body = email_data.get("body", {}).get("content", "") or email_data.get("bodyPreview", "")
        sender_info = email_data.get("sender", {}).get("emailAddress", {})
        sender_email = sender_info.get("address", "")
        sender_name = sender_info.get("name", "")
        received_at_raw = email_data.get("receivedDateTime")

        try:
            received_at = date_parser.parse(received_at_raw) if received_at_raw else datetime.now(timezone.utc)
        except (ValueError, OverflowError):
            received_at = datetime.now(timezone.utc)

        analysis = await self._analyze(subject, body, sender_email, received_at_raw or "")

        record = EmailRecord(
            message_id=email_data.get("id"),
            subject=subject,
            sender_email=sender_email,
            sender_name=sender_name,
            received_at=received_at,
            body_preview=email_data.get("bodyPreview") or body[:250],
            full_body=body,
            has_attachments=email_data.get("hasAttachments", False),
            outlook_message_id=email_data.get("id"),
        )
        self._apply_analysis(record, analysis)

        db.add(record)
        await db.commit()
        await db.refresh(record)

        await self._process_attachments(record, email_data.get("id"), db)
        await self._run_extraction_pipeline(record, db, auto_create=True)
        return record

    async def analyze_and_update(self, record, db):
        """Re-run AI analysis on an existing EmailRecord and persist the results."""
        was_unprocessed = record.processed_at is None

        analysis = await self._analyze(
            record.subject or "", record.full_body or "", record.sender_email or "", str(record.received_at)
        )
        self._apply_analysis(record, analysis)
        await db.commit()
        await db.refresh(record)

        await self._run_extraction_pipeline(record, db, auto_create=was_unprocessed)
        return record

    async def process_batch(self, emails: list, db) -> list:
        return [await self.process_and_store(e, db) for e in emails]

    async def categorize_email(self, subject: str, body: str) -> str:
        analysis = await self.agent._extract_json(
            "Categorize this email.", f"Subject: {subject}\nBody: {body}",
            {"type": "object", "properties": {"department": {"type": "string"}}},
        )
        return analysis.get("department", "General")

    async def detect_priority(self, subject: str, body: str, sender: str) -> str:
        analysis = await self.agent._extract_json(
            "Detect priority.", f"Subject: {subject}\nBody: {body}",
            {"type": "object", "properties": {"priority": {"type": "string"}}},
        )
        return analysis.get("priority", "MEDIUM")

    async def generate_summary(self, subject: str, body: str) -> str:
        return await self.agent.generate_summary(subject, body)

    async def generate_reply_suggestion(self, email_data: dict) -> str:
        return await self.agent.suggest_reply(
            email_data.get("subject", ""),
            email_data.get("body", {}).get("content", ""),
            email_data.get("sender", {}).get("emailAddress", {}).get("address", ""),
            {},
        )
