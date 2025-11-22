from uuid import UUID
import sqlalchemy
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.contacts.models import Contact
from modules.contacts.repositories import ContactRepository
from core.redis import redis_client
from modules.contacts.schemas import CreateContact, UpdateContact
from modules.wazzup.contacts import WazzupContacts


class ContactService:
    @staticmethod
    async def get_contacts(session: AsyncSession):
        contacts = await ContactRepository.get_all_contacts(session)
        return contacts
    
    @staticmethod
    async def create_contact(session: AsyncSession, contact_data: CreateContact, sync_to_wazzup: bool = True):
        contact_data = contact_data.model_dump()
        if contact_data.get("responsible_user_id") is None:
            contact_data["responsible_user_id"] = await redis_client.rpoplpush("employee_queue", "employee_queue")
        try:
            new_contact = await ContactRepository.create_contact(session, contact_data) 
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact with this number of tg_username already exists"
            )
        
        if sync_to_wazzup:
            contact_data_to_wazzup = []
            if contact_data.get("phone"):
                contact_data_to_wazzup.append({"chatType": "whatsapp", "chatId": contact_data["phone"]})
            if contact_data.get("telegram_username"):
                contact_data_to_wazzup.append({"chatType": "telegram", "username": contact_data["telegram_username"]})
            if contact_data.get("telegram_id"):
                contact_data_to_wazzup.append({"chatType": "telegram", "chatId": contact_data["telegram_id"]})
            wazzup = WazzupContacts()
            await wazzup.create_contact([{
                "id": str(new_contact.id),
                "responsibleUserId": str(new_contact.responsible_user_id),
                "name": f"{new_contact.first_name} {new_contact.last_name}",
                "contactData": contact_data_to_wazzup,
            }])

        return new_contact
    
    @staticmethod
    async def get_one_or_none(session: AsyncSession, **filter_by):
        return await ContactRepository.get_one_or_none(session, **filter_by)
    
    @staticmethod
    async def delete_contact(session: AsyncSession, id):
        contact = await ContactService.get_one_or_none(session, id=id)

        if not contact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
        deleted = await ContactRepository.delete_contact(session, id)
    
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error. Contact not deleted"
            )
        wazzup = WazzupContacts()
        await wazzup.delete_contact(contact.id)

    
    @staticmethod
    async def update_contact(session: AsyncSession, id: UUID, contact_data: UpdateContact) -> Contact:
        contact = await ContactService.get_one_or_none(session, id=id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        filtered_data = contact_data.model_dump(exclude_unset=True)
        updated_contact = await ContactRepository.update_contact(session, id, filtered_data)

        updated_data_to_wazzup = []
        if updated_contact.phone:
            updated_data_to_wazzup.append({"chatType": "whatsapp", "chatId": updated_contact.phone})
        if updated_contact.telegram_username:
            updated_data_to_wazzup.append({"chatType": "telegram", "username": updated_contact.telegram_username})
        if updated_contact.telegram_id:
            updated_data_to_wazzup.append({"chatType": "telegram", "chatId": updated_contact.telegram_id})
        wazzup = WazzupContacts()
        await wazzup.update_contact([{
            "id": str(updated_contact.id),
            "responsibleUserId": str(updated_contact.responsible_user_id),
            "name": f"{updated_contact.first_name} {updated_contact.last_name}",
            "contactData": updated_data_to_wazzup,
        }])

        return updated_contact
