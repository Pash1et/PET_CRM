from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/templates")

router = APIRouter(prefix="/ui/deals", tags=["UI Сделки"])

@router.get("/", response_class=HTMLResponse)
async def contacts_page(request: Request):
    return templates.TemplateResponse("deals/deals.html", {"request": request})
