from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.contacts.exceptions import ContactAlreadyExists, ContactDeleteError, ContactNotFound
from modules.contacts.schemas import ReadContact, CreateContact, UpdateContact
from modules.contacts.services import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReadContact])
async def get_contacts(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await ContactService.get_contacts(session)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadContact)
async def create_contact(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    contact_data: CreateContact,
):
    return await ContactService.create_contact(session, contact_data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    session: Annotated[AsyncSession, Depends(get_async_session)], 
    id: UUID,
):
    try:
        await ContactService.delete_contact(session, id)
    except ContactNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    except ContactDeleteError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact not deleted",
        )
    except ContactAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact already exists",
        )

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ReadContact)
async def update_contact(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
    contact_data: UpdateContact
):
    try:
        return await ContactService.update_contact(session, id, contact_data)
    except ContactNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
