from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_async_session
from modules.employees.dependencies import (get_current_employee,
                                            get_employee_service)
from modules.employees.exceptions import (EmployeeAlreadyExists,
                                          EmployeeDeleteError,
                                          EmployeeNotFound)
from modules.employees.models import Employee
from modules.employees.schemas import (CreateEmployee, LoginEmployee,
                                       ReadEmployee, Token, UpdateEmployee)
from modules.employees.services import AuthService, EmployeeService

employee_router = APIRouter(prefix="/employee", tags=["employees"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@employee_router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReadEmployee])
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
    try:
        await employee_service.delete_employee(id)
    except EmployeeNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    except EmployeeDeleteError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee cannot be deleted",
        )

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
    try:
        return await employee_service.create_employee(employee_data)
    except EmployeeAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already exists",
        )


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
    
    token = AuthService.create_access_token(employee.id)
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
