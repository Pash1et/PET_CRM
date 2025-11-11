from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from modules.deals.models import DealStage


class BaseDeal(BaseModel):
    title: str
    amount: Decimal | None = None
    contact_id: UUID | None


class DealCreate(BaseDeal):
    pass


class DealRead(BaseDeal):
    id: UUID
    stage: DealStage
    created_at: datetime
    updated_at: datetime


class DealUpdate(BaseDeal):
    title: str | None
    contact_id: UUID | None = None
    stage: DealStage | None = None
