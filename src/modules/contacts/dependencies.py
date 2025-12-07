from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from core.redis import redis_client
from modules.contacts.services import ContactService
from modules.wazzup.client import WazzupClient
from modules.wazzup.contacts import WazzupContacts
from modules.wazzup.dependencies import get_wazzup_client


def get_wazzup_contacts(
    client: Annotated[WazzupClient, Depends(get_wazzup_client)]
):
    return WazzupContacts(client)

def get_contact_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    wazzup_contacts: Annotated[WazzupContacts, Depends(get_wazzup_contacts)],
) -> ContactService:
    return ContactService(
        session=session,
        redis_client=redis_client,
        wazzup_contacts=wazzup_contacts,
    )
