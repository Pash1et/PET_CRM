from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.deals.exceptions import DealDeleteError, DealNotFound
from modules.deals.models import Deal, DealStage
from modules.deals.repositories import DealRepository
from modules.deals.schemas import CreateDeal, UpdateDeal
from modules.wazzup.deals import WazzupDeals


class DealService:

    def __init__(
        self,
        session: AsyncSession,
        wazzup_deals: WazzupDeals,
    ):
        self.session = session
        self.wazzup_deals = wazzup_deals

    async def get_deals(self) -> list[Deal]:
        return await DealRepository.get_all_deals(self.session)
    
    async def create_deal(self, deal_data: CreateDeal, sync_to_wazzup: bool = True) -> Deal:
        deal_data = deal_data.model_dump()
        new_deal = await DealRepository.create_deal(self.session, deal_data)

        if sync_to_wazzup:
            await self.wazzup_deals.create_deal([{
                "id": str(new_deal.id),
                "responsibleUserId": str(new_deal.responsible_user_id),
                "name": f"{new_deal.title}",
                "contacts": [str(new_deal.contact_id)],
                "closed": False,
            }])

        return new_deal
    
    async def get_one_or_none(self, id: UUID) -> Deal | None:
        return await DealRepository.get_one_or_none(self.session, id)
    
    async def delete_deal(self, id: UUID) -> None:
        deal = await self.get_one_or_none(id)
        if not deal:
            raise DealNotFound()

        deleted = await DealRepository.delete_deal(self.session, id)
        if not deleted:
            raise DealDeleteError()
        
        await self.wazzup_deals.delete_deal(deal.id)

    async def update_deal(self, id: UUID, deal_data: UpdateDeal) -> Deal:
        deal = await self.get_one_or_none(id)
        if not deal:
            raise DealNotFound()

        filtered_data = deal_data.model_dump(exclude_unset=True)
        updated_deal = await DealRepository.update_deal(self.session, id, filtered_data)

        closed = True if updated_deal.stage == DealStage.won or updated_deal.stage == DealStage.lost else False
        await self.wazzup_deals.update_deal([{
            "id": str(updated_deal.id),
            "responsibleUserId": str(updated_deal.responsible_user_id),
            "name": f"{updated_deal.title}",
            "contacts": [str(updated_deal.contact_id)],
            "uri": f"http://localhost:8000/api/v1/deals/{updated_deal.id}",
            "closed": closed,
        }])
        return updated_deal
        
