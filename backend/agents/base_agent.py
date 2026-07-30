import logging

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, openai_client):
        self.client = openai_client
        self.model = "gpt-4o"
    
    async def run(self, input_data: dict) -> dict:
        raise NotImplementedError
    
    async def _call_llm(self, system_prompt: str, user_message: str, temperature: float = 0.1) -> str:
        return await self.client.complete(
            system_prompt=system_prompt,
            user_message=user_message,
            model=self.model,
            temperature=temperature
        )
    
    async def _extract_json(self, system_prompt: str, user_message: str, schema_description: dict) -> dict:
        return await self.client.extract_structured(
            system_prompt=system_prompt,
            user_message=user_message,
            response_schema=schema_description
        )
