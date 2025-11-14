from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

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
    
    @staticmethod
    async def get_one_or_none(session: AsyncSession, id: UUID) -> Deal | None:
        query = select(Deal).where(Deal.id == id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_deal(session: AsyncSession, id: UUID) -> Deal:
        query = delete(Deal).where(Deal.id == id).returning(Deal)
        result = await session.execute(query)
        await session.commit()
        return result.scalar()
    
    @staticmethod
    async def update_deal(session: AsyncSession, id: UUID, deal_data: dict) -> Deal:
        query = update(Deal).where(Deal.id == id).values(**deal_data).returning(Deal)
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one()
