from sqlalchemy.ext.asyncio import AsyncSession
from modules.deals.repositories import DealRepository
from modules.deals.schemas import DealCreate


class DealService:
    @staticmethod
    async def get_deals(session: AsyncSession):
        deals = await DealRepository.get_all_deals(session)
        return deals
    
    @staticmethod
    async def create_deal(session: AsyncSession, deal_data: DealCreate):
        deal_data = deal_data.model_dump()
        new_deal = await DealRepository.create_deal(session, deal_data)
        return new_deal