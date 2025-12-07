from uuid import UUID

from modules.wazzup.client import WazzupClient


class WazzupDeals:
    BASE_URL = "/deals"

    def __init__(self):
        self.client = WazzupClient()

    async def create_deal(self, data: list):
        return await self.client.post(self.BASE_URL, data=data)
    
    async def delete_deal(self, id: UUID):
        return await self.client.delete(f"{self.BASE_URL}/{id}")
    
    async def update_deal(self, data: list):
        return await self.client.post(self.BASE_URL, data=data)
