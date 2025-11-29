from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from modules.contacts.schemas import CreateContact, UpdateContact
from modules.contacts.services import ContactService
from modules.deals.schemas import CreateDeal
from modules.deals.services import DealService

router = APIRouter(prefix="/wazzup", tags=["wazzup webhooks"])


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def webhook(req: Request, session: Annotated[AsyncSession, Depends(get_async_session)]):
    payload = await req.json()
    print(payload)
    if "createDeal" in payload:
        contact = await ContactService.get_one_or_none(session, id=payload["createDeal"]["contacts"][0])
        if contact:
            deal_data = CreateDeal(
                title=f"Сделка с контактом {contact.first_name} {contact.last_name}",
                contact_id=contact.id,
                responsible_user_id=payload["createDeal"]["responsibleUserId"]
            )
            new_deal = await DealService.create_deal(session, deal_data, sync_to_wazzup=False)
            return {
                "id": str(new_deal.id),
                "responsibleUserId": str(new_deal.responsible_user_id),
                "name": new_deal.title,
                "uri": f"http://localhsot:8000/api/v1/deals/{str(new_deal.id)}",
                "contacts": [str(new_deal.contact_id)],
                "closed": False,
            }
    if "createContact" in payload:
        contact = await ContactService.get_one_or_none(
            session,
            telegram_username=payload["createContact"]["contactData"][0].get("username"),
        )
        if not contact:
            full_name = payload["createContact"]["name"].split()
            contact_data = CreateContact(
                first_name=full_name[0],
                last_name=full_name[1] if len(full_name) > 1 else "",
                telegram_id=payload["createContact"]["contactData"][0].get("chatId"),
                telegram_username=payload["createContact"]["contactData"][0].get("username"),
                responsible_user_id=payload["createContact"]["responsibleUserId"],
            )
            new_contact = await ContactService.create_contact(session, contact_data, sync_to_wazzup=False)
            return {
                "id": str(new_contact.id),
                "responsibleUserId": str(new_contact.responsible_user_id),
                "name": f"{new_contact.first_name} {new_contact.last_name}",
                "contactData": [{
                    "chatType": payload["createContact"]["contactData"][0]["chatType"],
                    "chatId": payload["createContact"]["contactData"][0]["chatId"]
                }],
            }

    if "messages" in payload:
        chat_type = payload["messages"][0]["chatType"]
        chat_id = payload["messages"][0]["chatId"]
        contact_chat_id = payload["messages"][0]["contact"].get("chatId")
        if chat_type == "telegram" and contact_chat_id is None:
            contact = await ContactService.get_one_or_none(session, telegram_username=payload["messages"][0]["contact"]["username"])
            await ContactService.update_contact(session, contact.id, UpdateContact(telegram_id=chat_id))

    return {"status": "ok"}
