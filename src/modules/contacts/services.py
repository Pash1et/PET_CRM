from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.contacts.exceptions import ContactAlreadyExists, ContactDeleteError, ContactNotFound
from modules.contacts.models import Contact
from modules.contacts.repositories import ContactRepository
from core.redis import redis_client
from modules.contacts.schemas import CreateContact, UpdateContact
from modules.contacts.utils import build_wazzup_contact_data
from modules.wazzup.contacts import WazzupContacts


class ContactService:
    wazzup = WazzupContacts() # Подумать как лучше вынести в DI

    @staticmethod
    async def get_contacts(session: AsyncSession):
        contacts = await ContactRepository.get_all_contacts(session)
        return contacts

    @staticmethod
    async def create_contact(session: AsyncSession, contact_data: CreateContact, sync_to_wazzup: bool = True):
        contact_data = contact_data.model_dump(exclude_unset=True)
        is_exist = await ContactRepository.find_existing_contact(
            session,
            contact_data.get("phone"),
            contact_data.get("telegram_username"),
            contact_data.get("telegram_id"), 
        )
        if is_exist:
            raise ContactAlreadyExists()

        if contact_data.get("responsible_user_id") is None:
            contact_data["responsible_user_id"] = await redis_client.rpoplpush("employee_queue", "employee_queue")
        new_contact = await ContactRepository.create_contact(session, contact_data) 

        if sync_to_wazzup:
            wazzup_contact_data = build_wazzup_contact_data(new_contact)
            await ContactService.wazzup.create_contact(wazzup_contact_data)

        return new_contact
    
    @staticmethod
    async def get_one_or_none(session: AsyncSession, **filter_by):
        return await ContactRepository.get_one_or_none(session, **filter_by)
    
    @staticmethod
    async def delete_contact(session: AsyncSession, id: UUID):
        contact = await ContactService.get_one_or_none(session, id=id)

        if not contact:
            raise ContactNotFound()
    
        deleted = await ContactRepository.delete_contact(session, id)
    
        if not deleted:
            raise ContactDeleteError()

        await ContactService.wazzup.delete_contact(contact.id)

    @staticmethod
    async def update_contact(session: AsyncSession, id: UUID, contact_data: UpdateContact) -> Contact:
        contact = await ContactService.get_one_or_none(session, id=id)
        if not contact:
            raise ContactNotFound()
        
        filtered_data = contact_data.model_dump(exclude_unset=True)
        updated_contact = await ContactRepository.update_contact(session, id, filtered_data)

        wazzup_contact_data = build_wazzup_contact_data(updated_contact)
        await ContactService.wazzup.update_contact(wazzup_contact_data)

        return updated_contact
