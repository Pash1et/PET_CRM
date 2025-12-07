from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_async_session
from core.redis import redis_client
from modules.employees.exceptions import EmployeeForbidden, EmployeeLoginError
from modules.employees.models import Employee
from modules.employees.repositories import EmployeeRepository
from modules.employees.services import EmployeeService
from modules.wazzup.employees import WazzupEmployees


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
):
    return EmployeeService(
        session=session,
        redis_client=redis_client,
        wazzup_employee=WazzupEmployees(),
    )

async def get_admin(
    employee: Annotated[Employee, Depends(get_current_employee)],
):
    if not employee.is_admin:
        raise EmployeeForbidden()
    return employee
