from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.deals.models import Deal
from modules.deals.repositories import DealRepository
from modules.deals.schemas import CreateDeal, ReadDeal, UpdateDeal
from modules.wazzup.deals import WazzupDeals


class DealService:
    @staticmethod
    async def get_deals(session: AsyncSession) -> list[ReadDeal]:
        deals = await DealRepository.get_all_deals(session)
        return deals
    
    @staticmethod
    async def create_deal(session: AsyncSession, deal_data: CreateDeal, sync_to_wazzup: bool = True) -> ReadDeal:
        deal_data = deal_data.model_dump()
        new_deal = await DealRepository.create_deal(session, deal_data)

        if sync_to_wazzup:
            wazzup = WazzupDeals()
            await wazzup.create_deal([{
                "id": str(new_deal.id),
                "responsibleUserId": str(new_deal.responsible_user_id),
                "name": f"{new_deal.title}",
                "contacts": [str(new_deal.contact_id)],
                "closed": "false",
            }])

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
        
        wazzup = WazzupDeals()
        await wazzup.delete_deal(deal.id)

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

        wazzup = WazzupDeals()
        closed = True if updated_deal.stage == "won" or updated_deal.stage == "lost" else False
        await wazzup.update_deal([{
            "id": str(updated_deal.id),
            "responsibleUserId": str(updated_deal.responsible_user_id),
            "name": f"{updated_deal.title}",
            "contacts": [str(updated_deal.contact_id)],
            "uri": f"http://localhost:8000/api/v1/deals/{updated_deal.id}",
            "closed": closed,
        }])
        return updated_deal
        
