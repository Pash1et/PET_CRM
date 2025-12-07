class DealsUI {
    constructor() {
        this.columns = {
            new: document.getElementById('column-new'),
            in_progress: document.getElementById('column-in_progress'),
            won: document.getElementById('column-won'),
            lost: document.getElementById('column-lost'),
        };
        this.counters = {
            new: document.getElementById('count-new'),
            in_progress: document.getElementById('count-in_progress'),
            won: document.getElementById('count-won'),
            lost: document.getElementById('count-lost'),
        };
        this.emptyState = document.getElementById('empty-state');
        this.form = document.getElementById('deal-form');

        this.setupEventListeners();
        this.loadDeals();
        setInterval(() => this.loadDeals(), 10000);
    }

    setupEventListeners() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createDeal();
        });
    }

    async loadDeals() {
        this.emptyState.textContent = 'Загружаем сделки...';
        try {
            const response = await fetch('/api/v1/deals/');
            if (!response.ok) throw new Error('Failed to load deals');
            const deals = await response.json();
            this.renderDeals(deals);
        } catch (err) {
            this.emptyState.textContent = 'Не удалось загрузить сделки';
            console.error(err);
        }
    }

    async createDeal() {
        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData);
        data.amount = data.amount ? Number(data.amount) : null;
        data.contact_id = data.contact_id || null;

        try {
            const response = await fetch('/api/v1/deals/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                this.form.reset();
                this.loadDeals();
            } else {
                const error = await response.json();
                alert(`Ошибка: ${error.detail || 'Не удалось создать сделку'}`);
            }
        } catch (err) {
            alert('Ошибка сети при создании сделки');
            console.error(err);
        }
    }

    async deleteDeal(id) {
        if (!confirm('Удалить эту сделку?')) return;
        try {
            const response = await fetch(`/api/v1/deals/${id}`, { method: 'DELETE' });
            if (response.ok) {
                document.getElementById(`deal-${id}`)?.remove();
                this.renderEmptyState();
            } else {
                alert('Не удалось удалить сделку');
            }
        } catch (err) {
            alert('Ошибка сети при удалении сделки');
        }
    }

    renderDeals(deals) {
        Object.values(this.columns).forEach((col) => (col.innerHTML = ''));

        const grouped = { new: [], in_progress: [], won: [], lost: [] };
        deals.forEach((deal) => {
            const stage = grouped[deal.stage] ? deal.stage : 'new';
            grouped[stage].push(deal);
        });

        let total = 0;

        Object.entries(grouped).forEach(([stage, list]) => {
            const column = this.columns[stage];
            const counter = this.counters[stage];
            counter.textContent = list.length;
            total += list.length;

            if (!list.length) {
                column.innerHTML = '<div class="column-empty">Пока пусто</div>';
                return;
            }

            list.forEach((deal) => {
                const card = document.createElement('div');
                card.className = 'contact-card deal-card';
                card.id = `deal-${deal.id}`;

                card.innerHTML = `
                    <div>
                        <div class="deal-title">${this.escape(deal.title || 'Без названия')}</div>
                        <div class="deal-meta">
                            <span>Сумма: ${this.formatAmount(deal.amount)}</span>
                            <span>Контакт: ${this.escape(deal.contact_id || 'Не привязан')}</span>
                            <span>Обновлено: ${this.escape(deal.updated_at || deal.created_at || '')}</span>
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button class="delete" data-id="${deal.id}">Удалить</button>
                    </div>
                `;

                card.querySelector('.delete').addEventListener('click', () => {
                    this.deleteDeal(deal.id);
                });

                column.appendChild(card);
            });
        });

        this.emptyState.textContent = total === 0 ? 'Сделок нет' : '';
    }

    escape(str) {
        const div = document.createElement('div');
        div.textContent = str ?? '';
        return div.innerHTML;
    }

    formatAmount(amount) {
        if (amount === null || amount === undefined || amount === '') return 'Без суммы';
        const num = Number(amount);
        if (Number.isNaN(num)) return this.escape(String(amount));
        return `${num.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽`;
    }

    renderEmptyState() {
        const hasDeals = Object.values(this.columns).some((col) => col.children.length > 0);
        this.emptyState.textContent = hasDeals ? '' : 'Сделок нет';
    }
}

document.addEventListener('DOMContentLoaded', () => new DealsUI());
