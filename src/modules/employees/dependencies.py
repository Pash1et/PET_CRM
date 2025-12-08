from typing import Annotated

import jwt
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_async_session
from core.redis import redis_client
from modules.employees.exceptions import EmployeeForbidden, EmployeeLoginError
from modules.employees.models import Employee
from modules.employees.repositories import EmployeeRepository
from modules.employees.services import EmployeeService
from modules.wazzup.client import WazzupClient
from modules.wazzup.dependencies import get_wazzup_client
from modules.wazzup.employees import WazzupEmployees


async def get_wazzup_employees(
    client: Annotated[WazzupClient, Depends(get_wazzup_client)]
) -> WazzupEmployees:
    return WazzupEmployees(client)

def get_token(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise EmployeeLoginError(detail="Invalid credentials")
    return access_token

async def get_current_employee(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(get_token)]
):
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise EmployeeLoginError(detail="Could not validate credentials")
    except jwt.InvalidTokenError:
        raise EmployeeLoginError(detail="Could not validate credentials")
    user = await EmployeeRepository.get_one_or_none(session, id=user_id)
    if user is None:
        raise EmployeeLoginError(detail="Could not validate credentials")
    return user

def get_employee_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    wazzup_employee: Annotated[WazzupEmployees, Depends(get_wazzup_employees)],
):
    return EmployeeService(
        session=session,
        redis_client=redis_client,
        wazzup_employee=wazzup_employee,
    )

async def get_admin(
    employee: Annotated[Employee, Depends(get_current_employee)],
):
    if not employee.is_admin:
        raise EmployeeForbidden()
    return employee
