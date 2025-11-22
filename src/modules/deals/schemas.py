import uuid
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from modules.deals.models import DealStage


class BaseDeal(BaseModel):
    title: str
    amount: Decimal | None = None
    contact_id: UUID | None


class CreateDeal(BaseDeal):
    responsible_user_id: uuid.UUID | None = None


class ReadDeal(BaseDeal):
    id: UUID
    stage: DealStage
    created_at: datetime
    updated_at: datetime
    responsible_user_id: uuid.UUID | None

    class Config:
        from_attributes = True


class UpdateDeal(BaseDeal):
    title: str | None = None
    contact_id: UUID | None = None
    stage: DealStage | None = None
    responsible_user_id: uuid.UUID | None = None
