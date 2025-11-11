from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID

from modules.deals.models import DealStage


class BaseDeal(BaseModel):
    title: str
    amount: Decimal | None = None
    contact_id: UUID


class DealCreate(BaseDeal):
    pass


class DealRead(BaseDeal):
    id: UUID
    stage: DealStage
    created_at: datetime
    updated_at: datetime
