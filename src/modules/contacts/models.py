import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from modules.deals.models import Deal


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    phone: Mapped[str | None] = mapped_column(unique=True)
    telegram_username: Mapped[str | None] = mapped_column(unique=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    deals: Mapped[list["Deal"]] = relationship(back_populates="contact")
