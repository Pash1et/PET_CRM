from httpx import AsyncClient

from core.config import settings


class WazzupClient:
    BASE_URL = "https://api.wazzup24.com/v3"

    def __init__(self):
        self.client = AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.WAZZUP_API_KEY}",
            }
        )

    async def get(self, url: str):
        return await self.client.get(url=url)

    async def post(self, url: str, data: list | dict):
        return await self.client.post(url=url, json=data)

    async def delete(self, url: str):
        return await self.client.delete(url=url)
