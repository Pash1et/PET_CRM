from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.deals.services import DealService
from modules.wazzup.deals import WazzupDeals
from modules.wazzup.dependencies import get_wazzup_client


def get_wazzup_deals(
    client: Annotated[WazzupDeals, Depends(get_wazzup_client)]
):
    return WazzupDeals(client)


def get_deal_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    wazzup_deals: Annotated[WazzupDeals, Depends(get_wazzup_deals)],
) -> DealService:
    return DealService(
        session=session,
        wazzup_deals=wazzup_deals,
    )
