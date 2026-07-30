import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CalendarIntelligenceAgent(BaseAgent):
    async def resolve_meeting(self, extracted_meeting: dict, existing_events: list) -> dict:
        prompt = "Resolve the proposed meeting details into exact datetime structures, and check for conflicts with existing events."
        msg = f"Meeting Data: {extracted_meeting}\nExisting Events: {existing_events}"
        return await self._extract_json(prompt, msg, {"type": "object", "properties": {"resolved_start": {"type": "string"}, "resolved_end": {"type": "string"}, "has_conflict": {"type": "boolean"}}})
    
    async def generate_preparation_checklist(self, event: dict, documents: list) -> list:
        prompt = "Generate a preparation checklist for this executive meeting."
        msg = f"Event: {event}\nRelevant Docs: {documents}"
        res = await self._call_llm(prompt, msg)
        return [line.strip() for line in res.split("\n") if line.strip()]
    
    async def generate_meeting_talking_points(self, meeting_title: str, context: dict, documents: list) -> list:
        prompt = "Generate 3-5 talking points for the GVP for the following meeting."
        msg = f"Meeting: {meeting_title}\nContext: {context}\nDocs: {documents}"
        res = await self._call_llm(prompt, msg)
        return [line.strip() for line in res.split("\n") if line.strip()]
