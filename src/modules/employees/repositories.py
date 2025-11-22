from uuid import UUID

from sqlalchemy import delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from modules.employees.models import Employee


class EmployeeRepository:
    @staticmethod
    async def get_all_employees(session: AsyncSession, **filter_by) -> list[Employee]:
        query = select(Employee).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_one_or_none(session: AsyncSession, **filter_by) -> Employee | None:
        query = select(Employee).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_employee(session: AsyncSession, employee_data: dict) -> Employee:
        query = insert(Employee).values(**employee_data).returning(Employee)
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one()
    
    @staticmethod
    async def delete_employee(session: AsyncSession, id: UUID) -> Employee:
        query = delete(Employee).where(Employee.id == id).returning(Employee)
        result = await session.execute(query)
        await session.commit()
        return result.scalar()
    
    @staticmethod
    async def update_employee(session: AsyncSession, employee_id: UUID, employee_data: dict) -> Employee:
        query = update(Employee).where(Employee.id == employee_id).values(**employee_data).returning(Employee)
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one()
