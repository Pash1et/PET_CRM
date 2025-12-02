from datetime import datetime, timedelta
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from modules.employees.exceptions import (EmployeeAlreadyExists,
                                          EmployeeDeleteError,
                                          EmployeeNotFound)
from modules.employees.models import Employee
from modules.employees.repositories import EmployeeRepository
from modules.employees.schemas import UpdateEmployee
from modules.employees.utils import get_password_hash, verify_password
from modules.wazzup.employees import WazzupEmployees


class EmployeeService:

    def __init__(
        self,
        session: AsyncSession,
        redis_client: Redis,
        wazzup_employee: WazzupEmployees
    ):
        self.session = session
        self.redis_client = redis_client
        self.wazzup_employee = wazzup_employee

    async def create_employee(self, employee_data) -> Employee | None:
        employee_data = employee_data.model_dump()
        email = employee_data.get("email")
    
        employee = await EmployeeRepository.get_one_or_none(self.session, email=email)
        if employee:
            raise EmployeeAlreadyExists()

        new_employee = await EmployeeRepository.create_employee(self.session, {
            "first_name": employee_data.get("first_name"),
            "last_name": employee_data.get("last_name"),
            "email": email,
            "hashed_password": get_password_hash(employee_data.get("password")),
        })

        await self.redis_client.rpush("employee_queue", str(new_employee.id))

        await self.wazzup_employee.create_employee([{
            "id": str(new_employee.id),
            "name": f"{new_employee.first_name} {new_employee.last_name}"
        }])

        return new_employee
    
    async def get_employees(self) -> list[Employee]:
        return await EmployeeRepository.get_all_employees(self.session)
    
    async def delete_employee(self, employee_id: UUID) -> None:
        employee = await EmployeeRepository.get_one_or_none(self.session, id=employee_id)

        if not employee:
            raise EmployeeNotFound()
        
        deleted = await EmployeeRepository.delete_employee(self.session, employee_id)
        if not deleted:
            raise EmployeeDeleteError()

        await self.redis_client.lrem("employee_queue", 0, str(employee.id))
        
        await self.wazzup_employee.delete_employee(employee.id)

    async def update_employee(self, id: UUID, employee_data: UpdateEmployee) -> Employee | None:
        employee = await EmployeeRepository.get_one_or_none(self.session, id=id)
        if not employee:
            raise EmployeeNotFound()
        
        filtered_data = employee_data.model_dump(exclude_unset=True)
        updated_employee = await EmployeeRepository.update_employee(self.session, id, filtered_data)
        
        await self.wazzup_employee.update_employee([{
            "id": str(updated_employee.id),
            "name": f"{updated_employee.first_name} {updated_employee.last_name}"
        }])

        return updated_employee


class AuthService:
    @staticmethod
    async def authenticate_employee(session: AsyncSession, email: str, password: str) -> Employee | None:
        employee = await EmployeeRepository.get_one_or_none(session, email=email)

        if employee and verify_password(password, employee.hashed_password):
            return employee
        return None
    
    @staticmethod
    def create_access_token(employee_id: UUID) -> str:
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
