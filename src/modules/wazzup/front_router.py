from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from modules.contacts.dependencies import get_contact_service
from modules.contacts.services import ContactService
from modules.employees.dependencies import get_current_employee
from modules.employees.models import Employee
from modules.wazzup.client import WazzupClient
from modules.wazzup.dependencies import get_wazzup_client
from modules.wazzup.iframe import WazzupIframe
from modules.wazzup.unanswered_count import UnansweredCount

templates = Jinja2Templates(directory="src/templates")

router = APIRouter(prefix="/ui/wazzup", tags=["UI Wazzup"])


@router.get("/", response_class=HTMLResponse)
async def wazzup_global_widget(
    request: Request,
    employee: Annotated[Employee, Depends(get_current_employee)],
    client: Annotated[WazzupClient, Depends(get_wazzup_client)],
):
    wazzup = WazzupIframe(client)
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
    client: Annotated[WazzupClient, Depends(get_wazzup_client)],
):
    wazzup = UnansweredCount(client)
    res = await wazzup.get_unanswered_count(employee.id)
    count = str(res.json()["counterV2"])
    return count

@router.get("/chat-card/{id}", response_class=HTMLResponse)
async def wazzup_chat_card(
    request: Request,
    employee: Annotated[Employee, Depends(get_current_employee)],
    wazzup_client: Annotated[WazzupClient, Depends(get_wazzup_client)],
    contacts_service: Annotated[ContactService, Depends(get_contact_service)],
    id: UUID,
):
    contact = await contacts_service.get_one_or_none(id=id)
    wazzup = WazzupIframe(wazzup_client)
    res = await wazzup.get_iframe_url({
        "user": {
            "id": str(employee.id),
            "name": f"{employee.first_name} {employee.last_name}"
        },
        "scope": "card",
        "filter": [
        {
            "chatType": "telegram",
            "chatId": contact.telegram_id,
        }
    ]
    })
    iframe_url = res.json().get("url")
    return templates.TemplateResponse(
        "wazzup/wazzup.html",
        {"request": request, "wazzup_url": iframe_url},
    )