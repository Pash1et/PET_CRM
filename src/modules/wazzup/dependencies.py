from typing import AsyncGenerator
import httpx
from core.config import settings
from modules.wazzup.client import WazzupClient


async def get_wazzup_client() -> AsyncGenerator[WazzupClient, None]:
    async with httpx.AsyncClient(
        base_url=settings.BASE_WAZZUP_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.WAZZUP_API_KEY}",
        },
        timeout=httpx.Timeout(5.0, connect=3.0)
    ) as client:
        yield WazzupClient(client)
