import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class EmailIntelligenceAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the AI brain of the Executive Office for the Group Vice President of Dangote Group.
Your role is to analyze every email and extract structured intelligence.
The GVP oversees: Dangote Cement (DCP), Dangote Sugar, Dangote Salt, NASCON, Dangote Fertiliser,
Dangote Packaging, and other group entities. Key locations: Lagos, Abuja, Obajana, Gboko.

From each email, extract:
- meeting_requests: list of {title, proposed_date, proposed_time, location, attendees, agenda, priority,
  preparation_required, confidence_score}. confidence_score is your own confidence (0.0-1.0) that this is
  a genuine, actionable meeting request versus an ambiguous or offhand mention.
- reschedule_requests: list of {meeting_reference, new_date, new_time, reason} — ONLY when the message
  refers to moving, postponing, or rescheduling an EXISTING meeting/appointment (e.g. "move the meeting
  to Wednesday", "let's postpone the inspection till Friday"). meeting_reference should be a short phrase
  identifying which existing meeting this refers to (e.g. "Refinery Expansion meeting", "the inspection").
- action_items: list of {description, owner, deadline, priority, department}
- decisions: list of {description, made_by, context}
- commitments: list of {description, by_whom, deadline, context}
- risks: list of {description, severity, category}
- summary: concise 2-3 sentence executive summary
- priority_level: CRITICAL|HIGH|MEDIUM|LOW with reasoning
- department: which Dangote subsidiary/department this relates to
- requires_gvp_response: true|false
- suggested_reply: draft reply if response is needed, else null
- sentiment: POSITIVE|NEUTRAL|NEGATIVE|URGENT
"""

    async def analyze_email(self, subject: str, body: str, sender: str, received_at: str) -> dict:
        user_message = f"Sender: {sender}\nReceived: {received_at}\nSubject: {subject}\nBody:\n{body}"
        schema = {
            "type": "object",
            "properties": {
                "meeting_requests": {"type": "array", "items": {"type": "object"}},
                "reschedule_requests": {"type": "array", "items": {"type": "object"}},
                "action_items": {"type": "array", "items": {"type": "object"}},
                "decisions": {"type": "array", "items": {"type": "object"}},
                "commitments": {"type": "array", "items": {"type": "object"}},
                "risks": {"type": "array", "items": {"type": "object"}},
                "summary": {"type": "string"},
                "priority_level": {"type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]},
                "department": {"type": "string"},
                "requires_gvp_response": {"type": "boolean"},
                "suggested_reply": {"type": "string"},
                "sentiment": {"type": "string"}
            },
            "required": ["summary", "priority_level", "department", "requires_gvp_response", "sentiment"]
        }
        return await self._extract_json(self.SYSTEM_PROMPT, user_message, schema)
    
    async def generate_summary(self, subject: str, body: str) -> str:
        prompt = "Summarize the following executive email in 1-2 sentences."
        msg = f"Subject: {subject}\n\n{body}"
        return await self._call_llm(prompt, msg, temperature=0.2)
    
    async def suggest_reply(self, subject: str, body: str, sender: str, context: dict) -> str:
        prompt = "You are drafting a reply for the GVP. Keep it professional, brief, and decisive."
        msg = f"Original Email from {sender}:\nSubject: {subject}\n\n{body}\n\nContext/Directives:\n{context}"
        return await self._call_llm(prompt, msg, temperature=0.3)
