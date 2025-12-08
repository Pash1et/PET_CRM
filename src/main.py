from fastapi import FastAPI, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse

from exceptions import BaseProjectException
from modules.contacts.routers import router as contacts_router
from modules.deals.routers import router as deals_router
from modules.employees.routers import auth_router, employee_router
from modules.wazzup.routers import router as wazzup_router

app = FastAPI(title="CRM", version="0.0.1")

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