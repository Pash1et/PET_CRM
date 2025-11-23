from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.contacts.services import ContactService


templates = Jinja2Templates(directory="src/templates")

router = APIRouter(prefix="/ui/contacts", tags=["UI Контакты"])


@router.get("/", response_class=HTMLResponse)
async def contacts_page(request: Request):
    return templates.TemplateResponse("contacts/list.html", {"request": request})

@router.get("/partial", response_class=HTMLResponse)
async def contacts_partial(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    contacts = await ContactService.get_contacts(session)
    return templates.TemplateResponse(
        "contacts/partial_list.html",
        {"request": request, "contacts": contacts},
    )

@router.delete("/{id}", response_class=HTMLResponse)
async def delete_contact(
    id: UUID,
    session: AsyncSession = Depends(get_async_session),
):  
    await ContactService.delete_contact(session, id)
    return HTMLResponse(content="")
