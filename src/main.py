from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from exceptions import BaseProjectException
from modules.contacts.front_router import router as contacts_front_router
from modules.contacts.front_router import templates
from modules.contacts.routers import router as contacts_router
from modules.deals.routers import router as deals_router
from modules.employees.dependencies import get_current_employee
from modules.employees.routers import auth_router, employee_router
from modules.wazzup.front_router import router as wazzup_front_router
from modules.wazzup.routers import router as wazzup_router

app = FastAPI(title="CRM", version="0.0.1")
app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(contacts_front_router)
app.include_router(wazzup_front_router)

@app.get(
    "/ui",
    dependencies=[Depends(get_current_employee)],
    response_class=HTMLResponse,
)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/ui/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/")
async def check_health():
    return { "health": "OK" }

app.include_router(contacts_router, prefix="/api/v1")
app.include_router(deals_router, prefix="/api/v1")
app.include_router(employee_router, prefix="/api/v1")
app.include_router(wazzup_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

@app.exception_handler(BaseProjectException)
async def app_exception_handler(request: Request, exc: BaseProjectException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request: Request, exc: ResponseValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )