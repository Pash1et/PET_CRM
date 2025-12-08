from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from modules.deals.dependencies import get_deal_service
from modules.deals.schemas import CreateDeal, ReadDeal, UpdateDeal
from modules.deals.services import DealService
from modules.employees.dependencies import get_current_employee

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

@router.get(
    "/stats",
    dependencies=[Depends(get_current_employee)]
)
async def get_deals_stats(
    deals_service: Annotated[DealService, Depends(get_deal_service)],
):
    return await deals_service.get_deals_by_period()

@router.get(
    "/revenue",
    dependencies=[Depends(get_current_employee)],
)
async def get_revenue(
    deals_service: Annotated[DealService, Depends(get_deal_service)],
):
    return await deals_service.get_amount_deals_by_period()

@router.get(
    "/{id}",
    dependencies=[Depends(get_current_employee)],
    status_code=status.HTTP_200_OK,
    response_model=ReadDeal,
)
async def get_deal(
    deals_service: Annotated[DealService, Depends(get_deal_service)],
    id: UUID,
):
    return await deals_service.get_one_or_none(id=id)
