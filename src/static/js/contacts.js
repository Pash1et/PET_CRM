class ContactsUI {
    constructor() {
        this.list = document.getElementById('contacts-list');
        this.emptyState = document.getElementById('empty-state');
        this.form = document.getElementById('contact-form');

        this.setupEventListeners();
        this.loadContacts();

        setInterval(() => this.loadContacts(), 10000);
    }

    setupEventListeners() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createContact();
        });
    }

    async loadContacts() {
        try {
            const response = await fetch('/api/v1/contacts/');
            if (!response.ok) throw new Error('Ошибка загрузки');

            const contacts = await response.json();
            this.renderContacts(contacts);
        } catch (err) {
            this.emptyState.textContent = 'Ошибка загрузки контактов';
            console.error(err);
        }
    }

    async createContact() {
        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData);

        try {
            const response = await fetch('/api/v1/contacts/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                this.form.reset();
                this.loadContacts();
            } else {
                const error = await response.json();
                alert(`Ошибка: ${error.detail || 'Не удалось добавить'}`);
            }
        } catch (err) {
            alert('Ошибка сети');
            console.error(err);
        }
    }

    async deleteContact(id) {
        if (!confirm('Удалить контакт?')) return;

        try {
            const response = await fetch(`/api/v1/contacts/${id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                document.getElementById(`contact-${id}`)?.remove();
                this.renderEmptyState();
            } else {
                alert('Не удалось удалить');
            }
        } catch (err) {
            alert('Ошибка сети');
        }
    }

    renderContacts(contacts) {
    this.list.innerHTML = '';

    if (contacts.length === 0) {
        this.emptyState.textContent = 'Нет контактов';
        return;
    }

    this.emptyState.textContent = '';

    contacts.forEach(contact => {
        const card = document.createElement('div');
        card.className = 'contact-card';
        card.id = `contact-${contact.id}`;

        const fullName = `${this.escape(contact.first_name)} ${this.escape(contact.last_name)}`.trim() || 'Без имени';

        card.innerHTML = `
            <div>
                <div class="contact-name">${fullName}</div>
                <div class="contact-detail">
                    Telegram: @${this.escape(contact.telegram_username) || '—'}
                </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <a href="/ui/wazzup/chat-card/${contact.id}"
                   target="_blank"
                   class="open-chat"
                   title="Открыть чат в Wazzup">
                    Чат
                </a>
                <button class="delete" data-id="${contact.id}">Удалить</button>
            </div>
        `;

        const deleteBtn = card.querySelector('.delete');
        deleteBtn.addEventListener('click', () => {
            this.deleteContact(contact.id);
        });

        this.list.appendChild(card);
    });
}


    escape(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    renderEmptyState() {
        if (this.list.children.length === 0) {
            this.emptyState.textContent = 'Нет контактов';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ContactsUI();
});
