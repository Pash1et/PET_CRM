from modules.wazzup.client import WazzupClient


class WazzupIframe:
    BASE_URL = "/iframe"

    def __init__(self, client: WazzupClient):
        self.client = client

    async def get_iframe_url(self, data: dict):
        return await self.client.post(self.BASE_URL, data=data)
