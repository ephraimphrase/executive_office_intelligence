"""Chat service — wraps ExecutiveAssistantAgent."""
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

# In-memory conversation store (replace with Redis in production)
_conversations: dict = {}

async def process_chat_message(user_id: str, message: str, conversation_id: str | None, db: AsyncSession) -> dict:
    """Process a chat message and return AI response. There's one ongoing
    conversation thread per user (the GVP's executive assistant), so history
    is keyed by user_id — conversation_id is accepted for API compatibility
    and echoed back, but doesn't select a different thread."""
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    history = _conversations.get(user_id, [])
    history.append({'role': 'user', 'content': message, 'timestamp': datetime.now(timezone.utc).isoformat()})

    executed_action = None
    try:
        from agents.orchestrator import orchestrator
        result = await orchestrator.handle_chat(message, history, db)
        reply = result.get('reply', 'I understand. How can I help you further?')

        intent_result = await orchestrator.chat_agent.extract_intent(message)
        intent = intent_result.get('intent')
        if intent in ('CREATE_TASK', 'SCHEDULE_MEETING') and db is not None:
            schema = {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "title": {"type": "string"},
                    "deadline": {"type": "string"},
                    "priority": {"type": "string"},
                    "department": {"type": "string"},
                    "proposed_date": {"type": "string"},
                    "proposed_time": {"type": "string"},
                    "location": {"type": "string"},
                },
            }
            action_data = await orchestrator.chat_agent._extract_json(
                "Extract structured fields needed to perform this action from the user's message.",
                message, schema,
            )
            executed_action = await orchestrator.chat_agent.execute_action(intent, action_data, user_id, db)
            if executed_action.get("status") == "success":
                reply += f"\n\n✅ Done — {intent.replace('_', ' ').title()} created."
    except Exception as e:
        reply = f"I'm here to help. (AI service initialising: {str(e)[:100]})"

    history.append({'role': 'assistant', 'content': reply, 'timestamp': datetime.now(timezone.utc).isoformat()})
    _conversations[user_id] = history[-50:]  # keep last 50 messages

    return {
        'reply': reply,
        'conversation_id': conversation_id,
        'sources_used': [],
        'action_executed': executed_action,
    }

async def get_chat_history(user_id: str, limit: int = 50) -> list:
    return _conversations.get(user_id, [])[-limit:]

async def clear_chat_history(user_id: str) -> bool:
    _conversations.pop(user_id, None)
    return True

async def generate_chat_suggestions(user_id: str, db: AsyncSession) -> list:
    return [
        "What is on the GVP's schedule today?",
        "Show me all overdue tasks",
        "What decisions are pending implementation?",
        "Draft a reply to the most recent critical email",
        "Generate today's executive briefing summary",
        "What commitments are due this week?",
    ]
