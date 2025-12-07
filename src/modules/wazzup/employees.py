from uuid import UUID

from modules.wazzup.client import WazzupClient


class WazzupEmployees:
    BASE_URL = "/users"

    def __init__(self):
        self.client = WazzupClient()

    async def create_employee(self, data: list):
        return await self.client.post(self.BASE_URL, data=data)

    async def delete_employee(self, id: UUID):
        return await self.client.delete(f"{self.BASE_URL}/{id}")
    
    async def update_employee(self, data: list):
        return await self.client.post(self.BASE_URL, data=data)
