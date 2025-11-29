from uuid import UUID

from modules.wazzup.client import WazzupClient


class UnansweredCount:
    BASE_URL = "/unanswered"

    def __init__(self):
        self.client = WazzupClient()

    async def get_unanswered_count(self, user_id: UUID):
        return await self.client.get(f"{self.BASE_URL}/{user_id}")
