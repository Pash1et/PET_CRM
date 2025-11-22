from uuid import UUID

from modules.wazzup.client import WazzupClient


class WazzupContacts:
    BASE_URL = "/contacts"

    def __init__(self):
        self.cleint = WazzupClient()

    async def create_contact(self, data: list):
        return await self.cleint.post(self.BASE_URL, data=data)

    async def delete_contact(self, id: UUID):
        return await self.cleint.delete(f"{self.BASE_URL}/{id}")
    
    async def update_contact(self, data: list):
        return await self.cleint.post(self.BASE_URL, data=data)
