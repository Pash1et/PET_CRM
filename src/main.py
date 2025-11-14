from fastapi import FastAPI

from modules.contacts.routers import router as contacts_router
from modules.deals.routers import router as deals_router
from modules.employees.routers import router as employees_router

app = FastAPI(title="CRM", version="0.0.1")


@app.get("/")
async def check_health():
    return { "health": "OK" }

app.include_router(contacts_router, prefix="/api/v1")
app.include_router(deals_router, prefix="/api/v1")
app.include_router(employees_router, prefix="/api/v1")
