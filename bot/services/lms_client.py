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
                timeout=10.0
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
    
    async def get_health(self) -> dict:
        try:
            client = await self._get_client()
            resp = await client.get("/items/")
            resp.raise_for_status()
            items = resp.json()
            return {"healthy": True, "item_count": len(items)}
        except httpx.ConnectError as e:
            return {"healthy": False, "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"healthy": False, "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
