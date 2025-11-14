from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.employees.repositories import EmployeeRepository
from modules.employees.utils import Hasher


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
        return new_employee
    
    @staticmethod
    async def get_employees(session: AsyncSession):
        employees = await EmployeeRepository.get_all_employees(session)
        return employees
