from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.employees.schemas import CreateEmployee, ReadEmployee
from modules.employees.services import EmployeeService

router = APIRouter(prefix="/employee", tags=["employee"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReadEmployee])
async def get_employee(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    employees = await EmployeeService.get_employees(session)
    return employees

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadEmployee)
async def create_employee(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    employee_data: CreateEmployee,
):
    new_employee = await EmployeeService.create_employee(session, employee_data)
    return new_employee

@router.put("/")
async def update_employee():
    pass

@router.delete("/")
async def delete_employee():
    pass
