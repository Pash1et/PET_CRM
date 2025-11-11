from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.deals.schemas import DealCreate, DealRead, DealUpdate
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

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_deal(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
):
    await DealService.delete_deal(session, id)


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=DealRead)
async def update_contact(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
    deal_data: DealUpdate,
):
    updated_deal = await DealService.update_deal(session, id, deal_data)
    return updated_deal
