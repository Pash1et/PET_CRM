from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from modules.contacts.routers import router as contacts_router
from modules.deals.routers import router as deals_router
from modules.employees.routers import router as employees_router
from modules.wazzup.routers import router as wazzup_router

from modules.contacts.front_router import router as contacts_front_router
from modules.contacts.front_router import templates
from modules.wazzup.front_router import router as wazzup_front_router


app = FastAPI(title="CRM", version="0.0.1")
app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.include_router(contacts_front_router)
app.include_router(wazzup_front_router)

@app.get("/ui", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/")
async def check_health():
    return { "health": "OK" }

app.include_router(contacts_router, prefix="/api/v1")
app.include_router(deals_router, prefix="/api/v1")
app.include_router(employees_router, prefix="/api/v1")
app.include_router(wazzup_router, prefix="/api/v1")
