import logging

from app.integrations.openai_client import get_openai_client

from .briefing_agent import BriefingAgent
from .calendar_agent import CalendarIntelligenceAgent
from .chat_agent import ExecutiveAssistantAgent
from .email_agent import EmailIntelligenceAgent
from .task_agent import TaskIntelligenceAgent

logger = logging.getLogger(__name__)

_SEARCH_STOPWORDS = {
    "what", "when", "where", "who", "which", "how", "why", "the", "a", "an", "is", "are",
    "was", "were", "did", "does", "do", "on", "in", "at", "to", "for", "of", "with", "and",
    "or", "has", "have", "not", "been", "any", "all", "show", "me", "gvp", "please", "made",
    "regarding", "about", "there", "that", "this",
}


def _extract_search_keywords(message: str, max_keywords: int = 3) -> list[str]:
    """global_search does a plain ILIKE substring match, so passing it a
    whole question ("What decisions were made on the Refinery?") never
    matches anything — it needs actual keywords. Prefers capitalized /
    longer words since those are more likely to be the proper nouns
    (project names, locations) the user is actually asking about."""
    import re

    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]{2,}", message)
    candidates = [w for w in words if w.lower() not in _SEARCH_STOPWORDS]
    candidates.sort(key=lambda w: (w[0].isupper(), len(w)), reverse=True)

    seen: set[str] = set()
    keywords = []
    for word in candidates:
        lw = word.lower()
        if lw not in seen:
            seen.add(lw)
            keywords.append(word)
        if len(keywords) >= max_keywords:
            break
    return keywords


class EOISOrchestrator:
    def __init__(self):
        openai_client = get_openai_client()
        self.email_agent = EmailIntelligenceAgent(openai_client)
        self.calendar_agent = CalendarIntelligenceAgent(openai_client)
        self.task_agent = TaskIntelligenceAgent(openai_client)
        self.briefing_agent = BriefingAgent(openai_client)
        self.chat_agent = ExecutiveAssistantAgent(openai_client)
    
    async def process_communication(self, comm_type: str, data: dict, db) -> dict:
        logger.info(f"Processing communication of type {comm_type}")
        if comm_type == "email":
            return await self.email_agent.analyze_email(
                subject=data.get("subject", ""),
                body=data.get("body", ""),
                sender=data.get("sender", ""),
                received_at=data.get("received_at", "")
            )
        return {"status": "unsupported"}
    
    async def handle_chat(self, message: str, history: list, db) -> dict:
        context = await self._build_chat_context(message, db)
        return await self.chat_agent.chat(message, history, context)

    async def _build_chat_context(self, message: str, db) -> dict:
        """Give the chat assistant real visibility into the GVP's actual
        data — schedule, tasks, decisions, emails, risks — plus anything
        specifically relevant to the question via search. Without this, the
        assistant can't actually answer "What decisions were made on the
        Refinery?" or "What has the GVP not responded to?" no matter how
        good the underlying model is."""
        context: dict = {
            "today_events": [], "upcoming_events": [], "recent_tasks": [],
            "pending_decisions": [], "critical_emails": [], "open_risks": [],
            "search_results": [],
        }
        if db is None:
            return context

        def _val(x):
            return x.value if hasattr(x, "value") else x

        try:
            from datetime import datetime, timedelta

            from sqlalchemy import select

            from app.models.decision import Decision, DecisionStatus
            from app.models.email_record import EmailRecord
            from app.models.event import Event
            from app.models.risk import Risk, RiskSeverity, RiskStatus
            from app.models.task import Task, TaskStatus

            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            week_end = today_start + timedelta(days=7)

            today_res = await db.execute(
                select(Event).where(Event.start_datetime >= today_start, Event.start_datetime < today_end)
                .order_by(Event.start_datetime)
            )
            context["today_events"] = [
                {"title": e.title, "start": str(e.start_datetime), "location": e.location}
                for e in today_res.scalars().all()
            ]

            upcoming_res = await db.execute(
                select(Event).where(Event.start_datetime >= today_end, Event.start_datetime < week_end)
                .order_by(Event.start_datetime).limit(10)
            )
            context["upcoming_events"] = [
                {"title": e.title, "start": str(e.start_datetime)} for e in upcoming_res.scalars().all()
            ]

            task_res = await db.execute(
                select(Task).where(Task.status != TaskStatus.DONE).order_by(Task.due_date).limit(15)
            )
            context["recent_tasks"] = [
                {"title": t.title, "status": _val(t.status), "due_date": str(t.due_date), "priority": _val(t.priority)}
                for t in task_res.scalars().all()
            ]

            decision_res = await db.execute(
                select(Decision).where(Decision.status == DecisionStatus.PENDING_IMPLEMENTATION).limit(10)
            )
            context["pending_decisions"] = [
                {"description": d.description, "made_by": d.made_by, "status": _val(d.status)}
                for d in decision_res.scalars().all()
            ]

            email_res = await db.execute(
                select(EmailRecord).where(EmailRecord.is_high_priority == True)  # noqa: E712
                .order_by(EmailRecord.received_at.desc()).limit(10)
            )
            context["critical_emails"] = [
                {"subject": e.subject, "sender": e.sender_name, "summary": e.ai_summary, "status": _val(e.status)}
                for e in email_res.scalars().all()
            ]

            risk_res = await db.execute(
                select(Risk).where(
                    Risk.status == RiskStatus.OPEN,
                    Risk.severity.in_([RiskSeverity.CRITICAL, RiskSeverity.HIGH]),
                )
            )
            context["open_risks"] = [
                {"description": r.description, "severity": _val(r.severity)} for r in risk_res.scalars().all()
            ]

            # Targeted search based on keywords in the question — covers
            # "What documents mention Obajana?" / "decisions on the Refinery?"
            from app.services.search import global_search

            seen_keys: set = set()
            search_results: list = []
            for keyword in _extract_search_keywords(message):
                for hit in await global_search(keyword, "all", 5, db):
                    key = (hit.get("type"), hit.get("id"))
                    if key not in seen_keys:
                        seen_keys.add(key)
                        search_results.append(hit)
            context["search_results"] = search_results[:10]
        except Exception as e:
            logger.warning(f"Failed to build chat context: {e}")

        return context

orchestrator = EOISOrchestrator()
