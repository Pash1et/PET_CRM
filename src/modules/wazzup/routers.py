from fastapi import APIRouter, Request, status

router = APIRouter(prefix="/wazzup", tags=["wazzup webhooks"])


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def webhook(req: Request):
    payload = await req.json()
    print(payload)
    return {"status": "ok"}
