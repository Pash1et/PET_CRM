import httpx

from core.config import settings
from modules.wazzup.exceptions import WazzupApiError, WazzupTransportError


class WazzupClient:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client or httpx.AsyncClient(
            base_url=settings.BASE_WAZZUP_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.WAZZUP_API_KEY}",
            },
            timeout=httpx.Timeout(5.0, connect=3.0)
        )

    async def get(self, url: str):
        return await self._request("get", url)

    async def post(self, url: str, data: list | dict):
        return await self._request("post", url, json=data)

    async def delete(self, url: str):
        return await self._request("delete", url)

    async def _request(self, method: str, url: str, **kwargs):
        try:
            res = await self.client.request(method, url, **kwargs)
            res.raise_for_status()
            return res
        except httpx.HTTPStatusError as e:
            raise WazzupApiError(e.response.status_code, e.response.text) from e
        except httpx.HTTPError as e:
            raise WazzupTransportError("Wazzup transport error") from e
