"""Meeting intelligence service — AI-powered meeting document generation."""
from sqlalchemy.ext.asyncio import AsyncSession


async def generate_agenda_ai(meeting_id: str, context: dict, db: AsyncSession) -> list:
    """Generate AI meeting agenda."""
    try:
        from agents.orchestrator import orchestrator
        result = await orchestrator.email_agent.client._call_llm(
            system_prompt="You are an executive meeting coordinator for Dangote Group GVP.",
            user_message=f"Generate a structured agenda for: {context.get('title', 'Meeting')}. Context: {context}"
        )
        # Parse bullet points into list
        lines = [l.strip().lstrip('•-123456789. ') for l in result.split('\n') if l.strip()]
        return lines[:10]
    except Exception:
        return [
            "Opening and welcome",
            "Review of previous action items",
            "Main agenda items",
            "Any other business",
            "Next steps and action items",
            "Date of next meeting",
        ]

async def generate_minutes_ai(meeting_id: str, transcript: str, db: AsyncSession) -> str:
    """Generate structured meeting minutes from transcript."""
    try:
        from agents.orchestrator import orchestrator
        result = await orchestrator.email_agent.client._call_llm(
            system_prompt="You are the executive secretary for the Group Vice President of Dangote Group. Generate formal meeting minutes.",
            user_message=f"Generate formal meeting minutes from this transcript:\n\n{transcript[:3000]}"
        )
        return result
    except Exception:
        return f"Meeting minutes pending AI processing.\n\nTranscript provided: {len(transcript)} characters."

async def extract_actions_ai(meeting_id: str, content: str, db: AsyncSession) -> list:
    """Extract action items from meeting content."""
    try:
        from agents.orchestrator import orchestrator
        result = await orchestrator.email_agent.client._call_llm(
            system_prompt="Extract action items from meeting content as JSON array [{description, owner, deadline, priority}]",
            user_message=content[:2000]
        )
        import json
        import re
        match = re.search(r'\[.*?\]', result, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []
    except Exception:
        return []

async def extract_decisions_ai(meeting_id: str, content: str, db: AsyncSession) -> list:
    """Extract decisions from meeting content — powers the Decision Register."""
    try:
        from agents.orchestrator import orchestrator
        result = await orchestrator.email_agent.client._call_llm(
            system_prompt="Extract decisions made in this meeting as a JSON array [{description, made_by, context}]",
            user_message=content[:2000]
        )
        import json
        import re
        match = re.search(r'\[.*?\]', result, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []
    except Exception:
        return []
