from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from modules.deals.models import Deal


class DealRepository:
    @staticmethod
    async def get_all_deals(session: AsyncSession, **filter_by) -> list[Deal]:
        query = select(Deal).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()


    @staticmethod
    async def create_deal(session: AsyncSession, deal_data: dict) -> Deal:
        new_deal = Deal(**deal_data)
        session.add(new_deal)
        await session.commit()
        await session.refresh(new_deal)
        return new_deal
