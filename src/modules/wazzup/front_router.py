from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient

from modules.employees.dependencies import get_current_employee
from modules.employees.models import Employee
from modules.wazzup.iframe import WazzupIframe
from modules.wazzup.unanswered_count import UnansweredCount


templates = Jinja2Templates(directory="src/templates")

router = APIRouter(prefix="/ui/wazzup", tags=["UI Wazzup"])


@router.get("/", response_class=HTMLResponse)
async def wazzup_global_widget(
    request: Request,
    employee: Annotated[Employee, Depends(get_current_employee)]
):
    wazzup = WazzupIframe()
    res = await wazzup.get_iframe_url({
        "user": {
            "id": str(employee.id),
            "name": f"{employee.first_name} {employee.last_name}"
        },
        "scope": "global",
    })
    iframe_url = res.json().get("url")
    return templates.TemplateResponse(
        "wazzup/wazzup.html",
        {"request": request, "wazzup_url": iframe_url},
    )

@router.get("/unread-count", response_class=HTMLResponse)
async def unread_count_page(
    request: Request,
    employee: Annotated[Employee, Depends(get_current_employee)],
):
    wazzup = UnansweredCount()
    res = await wazzup.get_unanswered_count(employee.id)
    return f'<span id="wazzup-counter-inner">{res.json()["counterV2"]}</span>'

@router.get("/chat-card/{id}", response_class=HTMLResponse)
async def wazzup_chat_card(
    request: Request,
    employee: Annotated[Employee, Depends(get_current_employee)],
    id: UUID,
):
    async with AsyncClient() as client:
        res = await client.get(
            f"http://localhost:8000/api/v1/contacts/{id}",
        )
    wazzup = WazzupIframe()
    res = await wazzup.get_iframe_url({
        "user": {
            "id": str(employee.id),
            "name": f"{employee.first_name} {employee.last_name}"
        },
        "scope": "card",
        "filter": [
        {
            "chatType": "telegram",
            "chatId": res.json()["telegram_id"],
        }
    ]
    })
    iframe_url = res.json().get("url")
    return templates.TemplateResponse(
        "wazzup/wazzup.html",
        {"request": request, "wazzup_url": iframe_url},
    )