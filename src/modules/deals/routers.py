from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from modules.deals.dependencies import get_deal_service
from modules.deals.schemas import CreateDeal, ReadDeal, UpdateDeal
from modules.deals.services import DealService

router = APIRouter(prefix="/deals", tags=["Deals"])


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
    await deals_service.delete_deal(id)

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ReadDeal)
async def update_deal(
    deals_service: Annotated[DealService, Depends(get_deal_service)],
    id: UUID,
    deal_data: UpdateDeal,
):
    return await deals_service.update_deal(id, deal_data)
