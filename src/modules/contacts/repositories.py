from uuid import UUID

from sqlalchemy import delete, or_, select, update
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
    async def get_one_or_none(session: AsyncSession, **filter_by) -> Contact | None:
        query = select(Contact).filter_by(**filter_by)
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
        query = update(Contact).where(Contact.id == id).values(**contact_data).returning(Contact)
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one()
    
    @staticmethod
    async def find_existing_contact(
        session: AsyncSession,
        phone: str | None = None,
        telegram_username: str | None = None,
        telegram_id: str | None = None
    ) -> Contact | None:
        query = select(Contact)

        contact_data = []
        if phone:
            contact_data.append(Contact.phone == phone)
        if telegram_username:
            contact_data.append(Contact.telegram_username == telegram_username)
        if telegram_id:
            contact_data.append(Contact.telegram_id == telegram_id)

        if not contact_data:
            return None

        query = query.where(or_(*contact_data))
        result = await session.execute(query)
        return result.scalar_one_or_none()
