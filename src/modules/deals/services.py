from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.deals.models import Deal
from modules.deals.repositories import DealRepository
from modules.deals.schemas import CreateDeal, ReadDeal, UpdateDeal


class DealService:
    @staticmethod
    async def get_deals(session: AsyncSession) -> list[ReadDeal]:
        deals = await DealRepository.get_all_deals(session)
        return deals
    
    @staticmethod
    async def create_deal(session: AsyncSession, deal_data: CreateDeal) -> ReadDeal:
        deal_data = deal_data.model_dump()
        new_deal = await DealRepository.create_deal(session, deal_data)
        return new_deal
    
    @staticmethod
    async def get_one_or_none(session: AsyncSession, id: UUID) -> ReadDeal | None:
        return await DealRepository.get_one_or_none(session, id)
    
    @staticmethod
    async def delete_deal(session: AsyncSession, id: UUID) -> None:
        deal = await DealService.get_one_or_none(session, id)
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found",
            )

        deleted = await DealRepository.delete_deal(session, id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error. Deal not deleted",
            )
        

    @staticmethod
    async def update_deal(session: AsyncSession, id: UUID, deal_data: UpdateDeal) -> Deal:
        deal = await DealService.get_one_or_none(session, id)
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found",
            )

        filtered_data = deal_data.model_dump(exclude_unset=True)
        updated_deal = await DealRepository.update_deal(session, id, filtered_data)
        return updated_deal
        
