from httpx import AsyncClient
import sqlalchemy
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.contacts.models import Contact
from modules.contacts.repositories import ContactRepository
from core.redis import redis_client
from core.config import settings


class ContactService:
    @staticmethod
    async def get_contacts(session: AsyncSession):
        contacts = await ContactRepository.get_all_contacts(session)
        return contacts
    
    @staticmethod
    async def create_contact(session: AsyncSession, contact_data):
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
        contact_data = [
            {
                "chatType": "whatsapp",
                "chatId": new_contact.phone
            },
            {
                "chatType": "telegram",
                "phone": new_contact.phone,
                "username": new_contact.telegram_username.strip("@")
            }
        ]
        async with AsyncClient() as client:
            await client.post(
                "https://api.wazzup24.com/v3/contacts",
                headers = {
                    "Authorization": f"Bearer {settings.WAZZUP_API_KEY}"
                },
                json = [
                    {
                        "id": str(new_contact.id),
                        "responsibleUserId": str(new_contact.responsible_user_id),
                        "name": f"{new_contact.first_name} {new_contact.last_name}",
                        "contactData": contact_data
                    }
                ]
            )
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
        async with AsyncClient() as client:
            await client.delete(
                f"https://api.wazzup24.com/v3/contacts/{str(contact.id)}",
                headers = {
                    "Authorization": f"Bearer {settings.WAZZUP_API_KEY}"
                },
            )

    
    @staticmethod
    async def update_contact(session: AsyncSession, id, contact_data) -> Contact:
        contact = await ContactService.get_one_or_none(session, id=id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        filtered_data = contact_data.model_dump(exclude_unset=True)
        updated_contact = await ContactRepository.update_contact(session, id, filtered_data)
        return updated_contact
