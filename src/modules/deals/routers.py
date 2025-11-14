from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.deals.schemas import CreateDeal, ReadDeal, UpdateDeal
from modules.deals.services import DealService

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReadDeal])
async def get_deals(session: Annotated[AsyncSession, Depends(get_async_session)]):
    deals = await DealService.get_deals(session)
    return deals

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadDeal)
async def create_deal(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    deal: CreateDeal, 
):
    new_deal = await DealService.create_deal(session, deal)
    return new_deal

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
):
    await DealService.delete_deal(session, id)


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ReadDeal)
async def update_deal(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
    deal_data: UpdateDeal,
):
    updated_deal = await DealService.update_deal(session, id, deal_data)
    return updated_deal
