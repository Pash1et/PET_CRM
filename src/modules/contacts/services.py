from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from modules.contacts.exceptions import (ContactAlreadyExists,
                                         ContactDeleteError, ContactNotFound)
from modules.contacts.models import Contact
from modules.contacts.repositories import ContactRepository
from modules.contacts.schemas import CreateContact, UpdateContact
from modules.contacts.utils import build_wazzup_contact_data
from modules.wazzup.contacts import WazzupContacts
from modules.wazzup.exceptions import WazzupError, WazzupUnavailable


class ContactService:
    def __init__(
        self,
        session: AsyncSession,
        redis_client: Redis,
        wazzup_contacts: WazzupContacts
    ):
        self.session = session
        self.redis_client = redis_client
        self.wazzup_contacts = wazzup_contacts

    async def get_contacts(self) -> list[Contact]:
        contacts = await ContactRepository.get_all_contacts(self.session)
        return contacts

    async def create_contact(self, contact_data: CreateContact, sync_to_wazzup: bool = True) -> Contact:
        contact_data = contact_data.model_dump(exclude_unset=True)
        is_exist = await ContactRepository.find_existing_contact(
            self.session,
            contact_data.get("phone"),
            contact_data.get("telegram_username"),
            contact_data.get("telegram_id"), 
        )
        if is_exist:
            raise ContactAlreadyExists()

        if contact_data.get("responsible_user_id") is None:
            contact_data["responsible_user_id"] = await self.redis_client.rpoplpush("employee_queue", "employee_queue")
        new_contact = await ContactRepository.create_contact(self.session, contact_data) 

        if sync_to_wazzup:
            wazzup_contact_data = build_wazzup_contact_data(new_contact)
            try:
                await self.wazzup_contacts.create_contact(wazzup_contact_data)
            except WazzupError as e:
                # raise WazzupUnavailable()
                print("Wazzup sync failed, will retry", e) # TODO: Убрать принт и добавить логгер

        return new_contact
    
    async def get_one_or_none(self, **filter_by) -> Contact:
        contact = await ContactRepository.get_one_or_none(self.session, **filter_by)
        if not contact:
            raise ContactNotFound()
        return contact

    async def delete_contact(self, id: UUID) -> None:
        contact = await self.get_one_or_none(id=id)
    
        deleted = await ContactRepository.delete_contact(self.session, id)
    
        if not deleted:
            raise ContactDeleteError()
        
        try:
            await self.wazzup_contacts.delete_contact(contact.id)
        except WazzupError as e:
            print("Wazzup sync failed, will retry", e) # TODO: Убрать принт и добавить логгер

    async def update_contact(self, id: UUID, contact_data: UpdateContact) -> Contact:
        await self.get_one_or_none(id=id)

        filtered_data = contact_data.model_dump(exclude_unset=True)
        updated_contact = await ContactRepository.update_contact(self.session, id, filtered_data)

        wazzup_contact_data = build_wazzup_contact_data(updated_contact)
        try:
            await self.wazzup_contacts.update_contact(wazzup_contact_data)
        except WazzupError as e:
            print("Wazzup sync failed, will retry", e) # TODO: Убрать принт и добавить логгер

        return updated_contact
