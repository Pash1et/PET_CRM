from datetime import datetime, timedelta
from uuid import UUID
from httpx import AsyncClient
from fastapi import HTTPException, status
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from modules.employees.repositories import EmployeeRepository
from modules.employees.schemas import UpdateEmployee
from modules.employees.utils import Hasher
from core.redis import redis_client
from core.config import settings
from modules.wazzup.employees import WazzupEmployees


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

        wazzup = WazzupEmployees()
        await wazzup.create_employee([{
            "id": str(new_employee.id),
            "name": f"{new_employee.first_name} {new_employee.last_name}"
        }])

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
        
        wazzup = WazzupEmployees()
        await wazzup.delete_employee(employee.id)

    @staticmethod
    async def update_employee(session: AsyncSession, id: UUID, employee_data: UpdateEmployee):
        employee = await EmployeeRepository.get_one_or_none(session, id=id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found",
            )
        
        filtered_data = employee_data.model_dump(exclude_unset=True)
        updated_employee = await EmployeeRepository.update_employee(session, id, filtered_data)
        
        wazzup = WazzupEmployees()
        await wazzup.update_employee([{
            "id": str(updated_employee.id),
            "name": f"{updated_employee.first_name} {updated_employee.last_name}"
        }])

        return updated_employee


class AuthService:
    @staticmethod
    async def authenticate_employee(session: AsyncSession, email: str, password: str):
        employee = await EmployeeRepository.get_one_or_none(session, email=email)

        if employee and Hasher.verify_password(password, employee.hashed_password):
            return employee
        return None
    
    @staticmethod
    async def create_access_token(employee_id: UUID):
        to_encode = {
            "sub": str(employee_id),
            "exp": datetime.now() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        }

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM,
        )
        return encoded_jwt
