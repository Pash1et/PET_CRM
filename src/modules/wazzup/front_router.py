from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from modules.employees.dependencies import get_current_employee
from modules.employees.schemas import ReadEmployee
from modules.wazzup.iframe import WazzupIframe
from modules.wazzup.unanswered_count import UnansweredCount


templates = Jinja2Templates(directory="src/templates")

router = APIRouter(prefix="/ui/wazzup", tags=["UI Wazzup"])


@router.get("/", response_class=HTMLResponse)
async def wazzup_global_widget(
    request: Request,
    employee: Annotated[ReadEmployee, Depends(get_current_employee)]
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
    employee: Annotated[ReadEmployee, Depends(get_current_employee)],
):
    wazzup = UnansweredCount()
    res = await wazzup.get_unanswered_count(employee.id)
    count = str(res.json()["counterV2"])
    return count


