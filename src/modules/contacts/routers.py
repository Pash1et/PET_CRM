from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.contacts.schemas import ReadContact, CreateContact, UpdateContact
from modules.contacts.services import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReadContact])
async def get_contacts(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    contacts = await ContactService.get_contacts(session)
    return contacts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadContact)
async def create_contact(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    contact_data: CreateContact,
):
    new_contact = await ContactService.create_contact(session, contact_data)
    return new_contact

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    session: Annotated[AsyncSession, Depends(get_async_session)], 
    id: UUID,
):
    await ContactService.delete_contact(session, id)

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ReadContact)
async def update_contact(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    id: UUID,
    contact_data: UpdateContact
):
    upd_contact = await ContactService.update_contact(session, id, contact_data)
    return upd_contact