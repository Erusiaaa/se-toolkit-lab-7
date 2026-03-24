import httpx

class LmsClient:
    """Client for LMS Backend API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0
            )
        return self._client
    
    async def get_items(self) -> list[dict]:
        client = await self._get_client()
        resp = await client.get("/items/")
        resp.raise_for_status()
        return resp.json()
    
    async def get_pass_rates(self, lab: str) -> list[dict]:
        client = await self._get_client()
        resp = await client.get(f"/analytics/pass-rates?lab={lab}")
        resp.raise_for_status()
        return resp.json()
    
    async def get_learners(self) -> list[dict]:
        client = await self._get_client()
        resp = await client.get("/learners/")
        resp.raise_for_status()
        return resp.json()
    
    async def get_groups(self, lab: str) -> list[dict]:
        client = await self._get_client()
        resp = await client.get(f"/analytics/groups?lab={lab}")
        resp.raise_for_status()
        return resp.json()
    
    async def get_top_learners(self, lab: str, limit: int = 5) -> list[dict]:
        client = await self._get_client()
        resp = await client.get(f"/analytics/top-learners?lab={lab}&limit={limit}")
        resp.raise_for_status()
        return resp.json()
    
    async def get_completion_rate(self, lab: str) -> dict:
        client = await self._get_client()
        resp = await client.get(f"/analytics/completion-rate?lab={lab}")
        resp.raise_for_status()
        return resp.json()
    
    async def get_timeline(self, lab: str) -> list[dict]:
        client = await self._get_client()
        resp = await client.get(f"/analytics/timeline?lab={lab}")
        resp.raise_for_status()
        return resp.json()
    
    async def get_scores(self, lab: str) -> list[dict]:
        client = await self._get_client()
        resp = await client.get(f"/analytics/scores?lab={lab}")
        resp.raise_for_status()
        return resp.json()
    
    async def trigger_sync(self) -> dict:
        client = await self._get_client()
        resp = await client.post("/pipeline/sync", json={})
        resp.raise_for_status()
        return resp.json()
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
