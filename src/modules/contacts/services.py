import sqlalchemy
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.contacts.repositories import ContactRepository


class ContactService:
    @staticmethod
    async def get_contacts(session: AsyncSession):
        contacts = await ContactRepository.get_all_contacts(session)
        return contacts
    
    @staticmethod
    async def create_contact(session: AsyncSession, contact_data):
        contact_data = contact_data.model_dump()
        try:
            new_contact = await ContactRepository.create_contact(session, contact_data) 
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact with this number of tg_username already exists"
            )
        
        return new_contact
    
    @staticmethod
    async def get_one_or_none(session: AsyncSession, id):
        return await ContactRepository.get_one_or_none(session, id)
    
    @staticmethod
    async def delete_contact(session: AsyncSession, id):
        contact = await ContactService.get_one_or_none(session, id)

        if not contact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
        deleted = await ContactRepository.delete_contact(session, id)
    
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error. Contact not deleted"
            )

    
    @staticmethod
    async def update_contact(session: AsyncSession, id, contact_data):
        contact = await ContactService.get_one_or_none(session, id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # filtered_data = dict(
        #     filter(
        #         lambda x: x[1] is not None, contact_data.model_dump().items()
        #         )
        # )
        filtered_data = contact_data.model_dump(exclude_unset=True)
        updated_contact = await ContactRepository.update_contact(session, id, filtered_data)
        return updated_contact
