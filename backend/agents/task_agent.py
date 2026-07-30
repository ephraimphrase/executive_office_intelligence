from .base_agent import BaseAgent


class TaskIntelligenceAgent(BaseAgent):
    async def prioritize_tasks(self, tasks: list) -> list:
        prompt = "Prioritize the following list of tasks for the GVP based on urgency, impact, and executive level."
        msg = f"Tasks: {tasks}"
        res = await self._extract_json(prompt, msg, {"type": "object", "properties": {"prioritized_ids": {"type": "array", "items": {"type": "string"}}}})
        return res.get("prioritized_ids", [])
    
    async def estimate_duration(self, task_description: str) -> int:
        prompt = "Estimate the duration in hours needed to complete this task. Return ONLY a number."
        msg = f"Task: {task_description}"
        res = await self._call_llm(prompt, msg)
        try:
            return int(res.strip())
        except ValueError:
            return 1
    
    async def suggest_owner(self, task_description: str, available_users: list) -> str:
        prompt = "Suggest the best owner for this task from the available users. Return ONLY the user's name/ID."
        msg = f"Task: {task_description}\nUsers: {available_users}"
        return await self._call_llm(prompt, msg)
