from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.deals.exceptions import DealDeleteError, DealNotFound
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
    return await DealService.create_deal(session, deal)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
):
    try:
        await DealService.delete_deal(session, id)
    except DealNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )
    except DealDeleteError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deal cannot be deleted",
        )


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ReadDeal)
async def update_deal(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
    deal_data: UpdateDeal,
):
    try:
        return await DealService.update_deal(session, id, deal_data)
    except DealNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )
