from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_async_session
from modules.employees.dependencies import get_current_employee
from modules.employees.schemas import CreateEmployee, LoginEmployee, ReadEmployee, Token, UpdateEmployee
from modules.employees.services import AuthService, EmployeeService

employee_router = APIRouter(prefix="/employee", tags=["employees"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@employee_router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReadEmployee])
async def get_employee(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    employees = await EmployeeService.get_employees(session)
    return employees

@employee_router.put("/", status_code=status.HTTP_200_OK, response_model=ReadEmployee)
async def update_employee(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
    employee_data: UpdateEmployee,
):
    updated_employee = await EmployeeService.update_employee(session, id, employee_data)
    return updated_employee

@employee_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
):
    await EmployeeService.delete_employee(session, id)

@employee_router.get("/me", status_code=status.HTTP_200_OK, response_model=ReadEmployee)
async def get_me(
    employee: Annotated[ReadEmployee, Depends(get_current_employee)],
):
    return employee

@auth_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=ReadEmployee)
async def create_employee(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    employee_data: CreateEmployee,
):
    new_employee = await EmployeeService.create_employee(session, employee_data)
    return new_employee


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    credentials: LoginEmployee,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    employee = await AuthService.authenticate_employee(session, credentials.email, credentials.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    token = await AuthService.create_access_token(employee.id)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return Token(access_token=token, token_type="Bearer")


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    employee: Annotated[ReadEmployee, Depends(get_current_employee)],
):
    response.delete_cookie("access_token")
