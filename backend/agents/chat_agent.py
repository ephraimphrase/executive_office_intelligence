from .base_agent import BaseAgent


class ExecutiveAssistantAgent(BaseAgent):
    SYSTEM_PROMPT = """You are EOIS, the AI Executive Assistant for the Group Vice President of Dangote Group.
You have access to the GVP's full calendar, processed emails, tasks, commitments, decisions, and knowledge base.
Answer questions concisely and professionally. Always cite sources. Ask for confirmation before creating/modifying data.
"""
    
    async def chat(self, message: str, conversation_history: list, context: dict) -> dict:
        prompt = "Process the user message and respond."
        msg = f"History: {conversation_history}\nContext: {context}\nUser: {message}"
        schema = {
            "type": "object",
            "properties": {
                "reply": {"type": "string"},
                "actions_suggested": {"type": "array", "items": {"type": "string"}},
                "sources": {"type": "array", "items": {"type": "string"}}
            }
        }
        return await self._extract_json(self.SYSTEM_PROMPT + "\n" + prompt, msg, schema)
    
    async def extract_intent(self, message: str) -> dict:
        prompt = "Classify user intent into QUERY|CREATE_TASK|SCHEDULE_MEETING|DRAFT_EMAIL|GENERATE_REPORT|OTHER."
        schema = {"type": "object", "properties": {"intent": {"type": "string"}}}
        return await self._extract_json(self.SYSTEM_PROMPT, message, schema)
    
    async def execute_action(self, action_type: str, action_data: dict, owner_id, db) -> dict:
        """Perform the requested action against the real database, when supported."""
        if action_type == "CREATE_TASK" and db is not None:
            from app.services.task_service import TaskService

            if not action_data.get("description") and action_data.get("title"):
                action_data["description"] = action_data["title"]
            task_svc = TaskService()
            task = await task_svc.create_from_action_item(action_data, "CHAT", None, owner_id, db)
            return {"status": "success", "action": action_type, "task_id": str(task.id)}

        if action_type == "SCHEDULE_MEETING" and db is not None:
            from app.services.calendar_service import CalendarService

            cal_svc = CalendarService()
            event = await cal_svc.create_from_extraction(action_data, None, owner_id, db, source_type="MANUAL")
            return {"status": "success", "action": action_type, "event_id": str(event.id)}

        return {"status": "not_executed", "action": action_type,
                "message": f"'{action_type}' is not yet auto-executable from chat."}
