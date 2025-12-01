from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient

templates = Jinja2Templates(directory="src/templates")

router = APIRouter(prefix="/ui/contacts", tags=["UI Контакты"])


@router.get("/", response_class=HTMLResponse)
async def contacts_page(request: Request):
    return templates.TemplateResponse("contacts/list.html", {"request": request})

@router.get("/partial", response_class=HTMLResponse)
async def contacts_partial(
    request: Request,
):
    async with AsyncClient() as client:
        res = await client.get("http://localhost:8000/api/v1/contacts/")
    contacts = res.json()
    return templates.TemplateResponse(
        "contacts/partial_list.html",
        {"request": request, "contacts": contacts},
    )

@router.delete("/{id}", response_class=HTMLResponse)
async def delete_contact(
    id: UUID,
):  
    async with AsyncClient() as client:
        await client.delete(
            f"http://localhost:8000/api/v1/contacts/{id}",
        )
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
):
    form = await request.form()

    async with AsyncClient() as client:
        res = await client.post(
            "http://localhost:8000/api/v1/contacts/",
            json={
                "first_name": form.get("first_name"),
                "last_name": form.get("last_name"),
                "phone": form.get("phone"),
                "telegram_username": form.get("telegram_username"),
            }
        )
    contacts = res.json()

    return templates.TemplateResponse(
        "contacts/partial_list.html", {"request": request, "contacts": contacts}
    )
