from modules.contacts.models import Contact


def build_wazzup_contact_data(contact_data: Contact) -> list[dict]:
        wazzup_contact_data = []

        if contact_data.phone:
            wazzup_contact_data.append({"chatType": "whatsapp", "chatId": contact_data.phone})
        if contact_data.telegram_username:
            wazzup_contact_data.append({"chatType": "telegram", "username": contact_data.telegram_username})
        if contact_data.telegram_id:
            wazzup_contact_data.append({"chatType": "telegram", "chatId": contact_data.telegram_id})

        return [{
            "id": str(contact_data.id),
            "responsibleUserId": str(contact_data.responsible_user_id),
            "name": f"{contact_data.first_name} {contact_data.last_name}",
            "contactData": wazzup_contact_data,
        }]