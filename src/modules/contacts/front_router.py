from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.contacts.services import ContactService
from modules.contacts.schemas import CreateContact


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

@router.get("/create", response_class=HTMLResponse)
async def create_contact_page(request: Request):
    return templates.TemplateResponse(
        "contacts/create_form.html",
        {"request": request},
    )

@router.post("/", response_class=HTMLResponse)
async def create_contact(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    form = await request.form()

    data = CreateContact(
        first_name=form.get("first_name"),
        last_name=form.get("last_name"),
        phone=form.get("phone"),
        telegram_username=form.get("telegram_username"),
    )

    await ContactService.create_contact(session, data)

    contacts = await ContactService.get_contacts(session)

    return templates.TemplateResponse(
        "contacts/partial_list.html", {"request": request, "contacts": contacts}
    )
