from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.deals.services import DealService
from modules.wazzup.deals import WazzupDeals


def get_deal_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> DealService:
    return DealService(
        session=session,
        wazzup_deals=WazzupDeals(),
    )
