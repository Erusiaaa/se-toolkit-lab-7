import httpx
import asyncio

class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._client = None
    
    async def _get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                timeout=60.0
            )
        return self._client
    
    async def chat(self, messages: list, tools: list = None):
        client = await self._get_client()
        body = {"model": self.model, "messages": messages}
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        
        # Retry with backoff for rate limits
        for attempt in range(3):
            try:
                resp = await client.post("/chat/completions", json=body)
                if resp.status_code == 429:
                    await asyncio.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
        raise Exception("Max retries exceeded")
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
