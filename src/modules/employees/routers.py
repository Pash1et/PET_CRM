from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_async_session
from modules.employees.dependencies import (get_admin, get_current_employee,
                                            get_employee_service)
from modules.employees.models import Employee
from modules.employees.schemas import (CreateEmployee, LoginEmployee,
                                       ReadEmployee, Token, UpdateEmployee)
from modules.employees.services import AuthService, EmployeeService

employee_router = APIRouter(prefix="/employee", tags=["Employees"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@employee_router.get(
    "/",
    dependencies=[Depends(get_admin)],
    status_code=status.HTTP_200_OK,
    response_model=list[ReadEmployee],
)
async def get_employee(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
):
    return await employee_service.get_employees()

@employee_router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ReadEmployee)
async def update_employee(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    id: UUID,
    employee_data: UpdateEmployee,
):
    updated_employee = await employee_service.update_employee(id, employee_data)
    return updated_employee

@employee_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    id: UUID,
):
    await employee_service.delete_employee(id)

@employee_router.get("/me", status_code=status.HTTP_200_OK, response_model=ReadEmployee)
async def get_me(
    employee: Annotated[Employee, Depends(get_current_employee)],
):
    return employee

@auth_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=ReadEmployee)
async def create_employee(
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    employee_data: CreateEmployee,
):
    return await employee_service.create_employee(employee_data)

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    credentials: LoginEmployee,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    employee = await AuthService.authenticate_employee(session, credentials.email, credentials.password)
    
    token = AuthService.create_access_token(employee.id)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return Token(access_token=token, token_type="Bearer")


@auth_router.post(
    "/logout",
    dependencies=[Depends(get_current_employee)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(response: Response):
    response.delete_cookie("access_token")
