from uuid import UUID

from modules.wazzup.client import WazzupClient


class WazzupContacts:
    BASE_URL = "/contacts"

    def __init__(self, client: WazzupClient):
        self.client = client

    async def create_contact(self, data: list):
        return await self.client.post(self.BASE_URL, data=data)

    async def delete_contact(self, id: UUID):
        return await self.client.delete(f"{self.BASE_URL}/{id}")
    
    async def update_contact(self, data: list):
        return await self.client.post(self.BASE_URL, data=data)
