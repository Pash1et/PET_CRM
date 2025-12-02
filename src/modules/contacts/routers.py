from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from modules.contacts.dependencies import get_contact_service
from modules.contacts.exceptions import (ContactAlreadyExists,
                                         ContactDeleteError, ContactNotFound)
from modules.contacts.schemas import CreateContact, ReadContact, UpdateContact
from modules.contacts.services import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReadContact])
async def get_contacts(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
):
    return await contact_service.get_contacts()

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ReadContact)
async def get_contact(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    id: UUID,
):
    return await contact_service.get_one_or_none(id=id)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadContact)
async def create_contact(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    contact_data: CreateContact,
):
    try:
        return await contact_service.create_contact(contact_data)
    except ContactAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact already exists",
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    id: UUID,
):
    try:
        await contact_service.delete_contact(id)
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

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ReadContact)
async def update_contact(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    id: UUID,
    contact_data: UpdateContact
):
    try:
        return await contact_service.update_contact(id, contact_data)
    except ContactNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
