import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class BaseContact(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    telegram_username: str | None = None

    @field_validator("telegram_username")
    def check_telegram_username(cls, v):
        if v:
            if not v.startswith("@"):
                raise ValueError("Telegram username must start with @")
            return v
        

class CreateContact(BaseContact):
    first_name: str
    last_name: str


class UpdateContact(BaseContact):
    pass


class ReadContact(BaseContact):
    id: uuid.UUID
    updated_at: datetime
    created_at: datetime
    responsible_user_id: uuid.UUID | None
