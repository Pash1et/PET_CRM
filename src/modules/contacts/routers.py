from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from modules.contacts.dependencies import get_contact_service
from modules.contacts.schemas import CreateContact, ReadContact, UpdateContact
from modules.contacts.services import ContactService
from modules.employees.dependencies import get_admin, get_current_employee

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    dependencies=[Depends(get_current_employee)],
    status_code=status.HTTP_200_OK,
    response_model=list[ReadContact],
)
async def get_contacts(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
):
    return await contact_service.get_contacts()

@router.get(
    "/{id}",
    dependencies=[Depends(get_current_employee)],
    status_code=status.HTTP_200_OK,
    response_model=ReadContact,
)
async def get_contact(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    id: UUID,
):
    return await contact_service.get_one_or_none(id=id)

@router.post(
    "/",
    dependencies=[Depends(get_current_employee)],
    status_code=status.HTTP_201_CREATED,
    response_model=ReadContact,
)
async def create_contact(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    contact_data: CreateContact,
):
    return await contact_service.create_contact(contact_data)

@router.delete(
    "/{id}",
    dependencies=[Depends(get_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contact(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    id: UUID,
):
    await contact_service.delete_contact(id)

@router.put(
    "/{id}",
    dependencies=[Depends(get_current_employee)],
    status_code=status.HTTP_200_OK,
    response_model=ReadContact,
)
async def update_contact(
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    id: UUID,
    contact_data: UpdateContact
):
    return await contact_service.update_contact(id, contact_data)
