from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from modules.deals.dependencies import get_deal_service
from modules.deals.exceptions import DealDeleteError, DealNotFound
from modules.deals.schemas import CreateDeal, ReadDeal, UpdateDeal
from modules.deals.services import DealService

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReadDeal])
async def get_deals(deals_service: Annotated[DealService, Depends(get_deal_service)]):
    return await deals_service.get_deals()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadDeal)
async def create_deal(
    deals_service: Annotated[DealService, Depends(get_deal_service)],
    deal: CreateDeal, 
):
    return await deals_service.create_deal(deal)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deals_service: Annotated[DealService, Depends(get_deal_service)],
    id: UUID,
):
    try:
        await deals_service.delete_deal(id)
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
    deals_service: Annotated[DealService, Depends(get_deal_service)],
    id: UUID,
    deal_data: UpdateDeal,
):
    try:
        return await deals_service.update_deal(id, deal_data)
    except DealNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )
