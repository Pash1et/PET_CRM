from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from modules.wazzup.iframe import WazzupIframe
from modules.wazzup.unanswered_count import UnansweredCount


templates = Jinja2Templates(directory="src/templates")

router = APIRouter(prefix="/ui/wazzup", tags=["UI Wazzup"])


@router.get("/", response_class=HTMLResponse)
async def wazzup_page(request: Request):
    wazzup = WazzupIframe()
    res = await wazzup.get_iframe_url({
        "user": {
            "id": "94390b09-b3e6-44bb-9b91-d9f495a74fa4",
            "name": "Dmitry Gorelov"
        },
        "scope": "global",
    })
    iframe_url = res.json().get("url")
    return templates.TemplateResponse(
        "wazzup/wazzup.html",
        {"request": request, "wazzup_url": iframe_url},
    )

@router.get("/unread-count", response_class=HTMLResponse)
async def unread_count_page(request: Request):
    wazzup = UnansweredCount()
    res = await wazzup.get_unanswered_count("94390b09-b3e6-44bb-9b91-d9f495a74fa4")
    return f'<span id="wazzup-counter-inner">{res.json()["counterV2"]}</span>'


