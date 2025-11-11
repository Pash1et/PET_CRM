from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.deals.schemas import DealCreate, DealRead
from modules.deals.services import DealService

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[DealRead])
async def get_deals(session: Annotated[AsyncSession, Depends(get_async_session)]):
    deals = await DealService.get_deals(session)
    return deals

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DealRead)
async def create_deal(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    deal: DealCreate, 
):
    new_deal = await DealService.create_deal(session, deal)
    return new_deal
