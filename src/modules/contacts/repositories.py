from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.contacts.models import Contact


class ContactRepository:
    @staticmethod
    async def get_all_contacts(session: AsyncSession, **filter_by) -> list[Contact]:
        query = select(Contact).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_contact(session: AsyncSession, contact_data) -> Contact:
        new_contact = Contact(**contact_data)
        session.add(new_contact)
        await session.commit()
        await session.refresh(new_contact)
        return new_contact
    
    @staticmethod
    async def get_one_or_none(session: AsyncSession, id: UUID) -> Contact | None:
        query = select(Contact).filter_by(id=id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_contact(session: AsyncSession, id: UUID) -> int:
        query = delete(Contact).where(Contact.id == id)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount

    @staticmethod
    async def update_contact(session: AsyncSession, id: UUID, contact_data) -> Contact:
        query = update(Contact).where(Contact.id == id).values(**contact_data)
        await session.execute(query)
        await session.commit()
        
        updated_contact = await session.get(Contact, id)
        return updated_contact
