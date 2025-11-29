import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class BaseContact(BaseModel):
    first_name: str | None = None
    last_name: str | None = ""
    phone: str | None = None
    telegram_username: str | None = None
    telegram_id: str | None = None
    responsible_user_id: uuid.UUID | None = None
        

class CreateContact(BaseContact):
    first_name: str
    last_name: str | None = None

    @field_validator("*", mode="before")
    def empty_fields_to_none(cls, v, info):
        if info.field_name == "last_name":
            return v
        if v == "":
            return None
        else:
            return v


class UpdateContact(BaseContact):
    pass


class ReadContact(BaseContact):
    id: uuid.UUID
    updated_at: datetime
    created_at: datetime
