import sys
from services.lms_client import LmsClient

class IntentRouter:
    def __init__(self, llm_client, lms_client):
        self.llm_client = llm_client
        self.lms_client = lms_client
    
    async def route(self, user_message: str) -> str:
        msg = user_message.lower()
        if "lab" in msg and ("list" in msg or "available" in msg or "what" in msg):
            items = await self.lms_client.get_items()
            labs = [i for i in items if i.get("type") == "lab"]
            titles = [l["title"] for l in labs]
            return "Available Labs: " + ", ".join(titles)
        if "hello" in msg or "hi" in msg:
            return "Hello! I am your LMS assistant. Ask me about labs or use /help."
        if "help" in msg:
            return "I can help with labs and scores. Use /help for commands."
        return "I did not understand. Try asking about labs or use /help."
