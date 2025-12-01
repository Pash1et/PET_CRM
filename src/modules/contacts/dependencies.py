from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from core.redis import redis_client
from modules.contacts.services import ContactService
from modules.wazzup.contacts import WazzupContacts


def get_contact_service(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> ContactService:
    wazzup = WazzupContacts()
    return ContactService(
        session=session,
        redis_client=redis_client,
        wazzup_contacts=wazzup,
    )
