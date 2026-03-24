import httpx

class LmsClient:
    """Client for LMS Backend API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0
            )
        return self._client
    
    async def get_items(self) -> list[dict]:
        client = await self._get_client()
        resp = await client.get("/items/")
        resp.raise_for_status()
        return resp.json()
    
    async def get_health(self) -> bool:
        try:
            client = await self._get_client()
            resp = await client.get("/items/")
            return resp.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        if self._client:
            await self._client.aclose()
