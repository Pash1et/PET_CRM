from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from modules.contacts.dependencies import get_contact_service
from modules.contacts.schemas import CreateContact, UpdateContact
from modules.contacts.services import ContactService
from modules.deals.dependencies import get_deal_service
from modules.deals.schemas import CreateDeal
from modules.deals.services import DealService
from modules.employees.dependencies import get_current_employee
from modules.employees.models import Employee
from modules.wazzup.client import WazzupClient
from modules.wazzup.dependencies import get_wazzup_client
from modules.wazzup.iframe import WazzupIframe
from modules.wazzup.unanswered_count import UnansweredCount

router = APIRouter(prefix="/wazzup", tags=["Wazzup"])


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def webhook(
    req: Request,
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
    deals_service: Annotated[DealService, Depends(get_deal_service)],
):
    payload = await req.json()
    print(payload)
    if "createDeal" in payload:
        contact = await contact_service.get_one_or_none(id=payload["createDeal"]["contacts"][0])
        if contact:
            deal_data = CreateDeal(
                title=f"Сделка с контактом {contact.first_name} {contact.last_name}",
                contact_id=contact.id,
                responsible_user_id=payload["createDeal"]["responsibleUserId"]
            )
            new_deal = await deals_service.create_deal(deal_data, sync_to_wazzup=False)
            return {
                "id": str(new_deal.id),
                "responsibleUserId": str(new_deal.responsible_user_id),
                "name": new_deal.title,
                "uri": f"http://localhsot:8000/api/v1/deals/{str(new_deal.id)}",
                "contacts": [str(new_deal.contact_id)],
                "closed": False,
            }
    if "createContact" in payload:
        contact = await contact_service.get_one_or_none(
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
            new_contact = await contact_service.create_contact(contact_data, sync_to_wazzup=False)
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
            contact = await contact_service.get_one_or_none(telegram_username=payload["messages"][0]["contact"]["username"])
            await contact_service.update_contact(contact.id, UpdateContact(telegram_id=chat_id))

    return {"status": "ok"}

@router.get("/unread-count")
async def get_unread_count(
    employee: Annotated[Employee, Depends(get_current_employee)],
    wazzup_client: Annotated[WazzupClient, Depends(get_wazzup_client)],
):
    wazzup = UnansweredCount(wazzup_client)
    res = await wazzup.get_unanswered_count(employee.id)
    count = res.json()["counterV2"]
    return count

@router.get("/wazzup-global-widget")
async def get_wazzup_global_widget(
    employee: Annotated[Employee, Depends(get_current_employee)],
    wazzup_client: Annotated[WazzupClient, Depends(get_wazzup_client)],
): 
    wazzup = WazzupIframe(wazzup_client)
    res = await wazzup.get_iframe_url({
        "user": {
            "id": str(employee.id),
            "name": f"{employee.first_name} {employee.last_name}"
        },
        "scope": "global",
    })
    iframe_url = res.json()
    return iframe_url

@router.get("/wazzup-card-widget/{id}")
async def get_wazzup_card_widget(
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
    iframe_url = res.json()
    return iframe_url
