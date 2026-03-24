import httpx
import json

class LLMClient:
    """Client for LLM API (OpenRouter compatible)."""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/Erusiaaa/se-toolkit-lab-7",
                },
                timeout=120.0
            )
        return self._client
    
    async def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        client = await self._get_client()
        body = {"model": self.model, "messages": messages}
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        resp = await client.post("/chat/completions", json=body)
        resp.raise_for_status()
        return resp.json()
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
