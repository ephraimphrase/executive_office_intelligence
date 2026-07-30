from .base_agent import BaseAgent


class BriefingAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the AI Chief of Staff for the Group Vice President of Dangote Group.
Generate concise, action-oriented executive briefings. 
Write in a professional tone suitable for a Fortune 100 executive.
Be specific, not generic. Reference actual meeting names, people, and projects.
"""
    
    async def generate_talking_points(self, meeting: dict, context: dict) -> list:
        prompt = "Generate 3-5 strategic talking points for this meeting."
        msg = f"Meeting: {meeting}\nContext: {context}"
        res = await self._call_llm(self.SYSTEM_PROMPT + "\n" + prompt, msg)
        return [line.strip() for line in res.split("\n") if line.strip()]
    
    async def generate_daily_priorities(self, events: list, tasks: list, emails: list, risks: list) -> list:
        prompt = "Synthesize the provided data to generate the top 5 strategic priorities for the day."
        msg = f"Events: {events}\nTasks: {tasks}\nEmails: {emails}\nRisks: {risks}"
        res = await self._call_llm(self.SYSTEM_PROMPT + "\n" + prompt, msg)
        return [line.strip() for line in res.split("\n") if line.strip()]
    
    async def generate_risk_summary(self, risks: list) -> str:
        prompt = "Write an executive summary of the current active risks."
        msg = f"Risks: {risks}"
        return await self._call_llm(self.SYSTEM_PROMPT + "\n" + prompt, msg)
    
    async def generate_executive_narrative(self, briefing_data: dict) -> str:
        prompt = "Write a 2-paragraph opening narrative for today's briefing pack."
        msg = f"Briefing Data: {briefing_data}"
        return await self._call_llm(self.SYSTEM_PROMPT + "\n" + prompt, msg)
