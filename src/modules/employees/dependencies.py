from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_async_session
from modules.employees.repositories import EmployeeRepository


def get_token(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return access_token


async def get_current_employee(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(get_token)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = await EmployeeRepository.get_one_or_none(session, id=user_id)
    if user is None:
        raise credentials_exception
    return user
