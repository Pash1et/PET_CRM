from uuid import UUID
from httpx import AsyncClient
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.employees.repositories import EmployeeRepository
from modules.employees.utils import Hasher
from core.redis import redis_client
from core.config import settings


class EmployeeService:
    @staticmethod
    async def create_employee(session, employee_data):
        employee_data = employee_data.model_dump()
        email = employee_data.get("email")
        
        employee = await EmployeeRepository.get_one_or_none(session, email=email)
        if employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee alreary register"
            )
        
        hashed_password = Hasher.get_password_hash(employee_data.get("password"))

        new_employee = await EmployeeRepository.create_employee(session, {
            "first_name": employee_data.get("first_name"),
            "last_name": employee_data.get("last_name"),
            "email": email,
            "hashed_password": hashed_password,
        })
        await redis_client.rpush("employee_queue", str(new_employee.id))
        async with AsyncClient() as client:
            await client.post(
                "https://api.wazzup24.com/v3/users",
                headers = {
                    "Authorization": f"Bearer {settings.WAZZUP_API_KEY}"
                },
                json = [
                    {
                        "id": str(new_employee.id),
                        "name": f"{new_employee.first_name} {new_employee.last_name}"
                    }
                ]
            )
        return new_employee
    
    @staticmethod
    async def get_employees(session: AsyncSession):
        employees = await EmployeeRepository.get_all_employees(session)
        return employees
    
    @staticmethod
    async def delete_employee(session: AsyncSession, employee_id: UUID):
        employee = await EmployeeRepository.get_one_or_none(session, id=employee_id)

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        deleted = await EmployeeRepository.delete_employee(session, employee_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error. Employee not deleted"
            )

        await redis_client.lrem("employee_queue", 0, str(employee.id))
        
        async with AsyncClient() as client:
            await client.delete(
                f"https://api.wazzup24.com/v3/users/{str(employee.id)}",
                headers = {
                    "Authorization": f"Bearer {settings.WAZZUP_API_KEY}"
                },
            )

    @staticmethod
    async def pull_employee(session: AsyncSession):
        async with AsyncClient() as client:
            res = await client.get(
                "https://api.wazzup24.com/v3/users/",
                headers = {
                    "Authorization": f"Bearer {settings.WAZZUP_API_KEY}"
                }
            )

            for employee in res.json():
                if not await EmployeeRepository.get_one_or_none(session, id=employee.get("id")):
                    await EmployeeRepository.create_employee(session, {
                        "id": employee.get("id"),
                        "first_name": employee.get("name").split(" ")[0],
                        "last_name": employee.get("name").split(" ")[1],
                        "email": f"{employee.get("id")}@CRM.com",
                        "hashed_password": "PASS123"
                        }
                    )
                    await redis_client.rpush("employee_queue", employee.get("id"))
