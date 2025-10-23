(function () {
    const API_BASE = '/api';
    const monthNames = [
        'Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni',
        'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December'
    ];

    function getToken() {
        return localStorage.getItem('access_token');
    }

    function requireAuth() {
        if (!getToken()) {
            window.location.href = '/login';
        }
    }

    async function fetchAPI(endpoint, options = {}) {
        const token = getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
            throw new Error('Niet geautoriseerd');
        }
        if (!response.ok) {
            let message = `API-fout (${response.status})`;
            try {
                const errorData = await response.json();
                if (errorData && errorData.detail) {
                    message = Array.isArray(errorData.detail)
                        ? errorData.detail.map(item => item.msg || item).join(', ')
                        : errorData.detail;
                }
            } catch (err) {
                // ignore json parse errors
            }
            throw new Error(message);
        }
        if (response.status === 204) {
            return null;
        }
        const text = await response.text();
        return text ? JSON.parse(text) : null;
    }

    function setFeedback(elementId, message, isError = false) {
        const element = document.getElementById(elementId);
        if (!element) return;
        element.textContent = message;
        element.classList.toggle('error', Boolean(message) && isError);
        element.classList.toggle('success', Boolean(message) && !isError);
    }

    function populateYearSelect(select, year) {
        if (!select) return;
        const years = [];
        const current = new Date().getFullYear();
        const baseYear = year && year > current ? year : current;
        for (let i = 0; i < 6; i += 1) {
            years.push(baseYear - i);
        }
        select.innerHTML = '';
        years.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            select.appendChild(option);
        });
        select.value = year || current;
    }

    function ensureYearOption(select, year) {
        if (!select) return;
        const optionExists = Array.from(select.options).some(opt => Number(opt.value) === Number(year));
        if (!optionExists) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            select.appendChild(option);
        }
        select.value = year;
    }

    function populateMonthSelect(select) {
        if (!select) return;
        select.innerHTML = '';
        monthNames.forEach((name, index) => {
            const option = document.createElement('option');
            option.value = String(index + 1);
            option.textContent = name;
            select.appendChild(option);
        });
        select.value = String(new Date().getMonth() + 1);
    }

    function renderCarInputs(cars) {
        const container = document.getElementById('car-entries');
        if (!container) return;
        container.innerHTML = '';
        if (!cars.length) {
            const message = document.createElement('p');
            message.textContent = 'Geen auto\'s geconfigureerd. Voeg ze toe op de beheerpagina.';
            container.appendChild(message);
            return;
        }
        cars.forEach(car => {
            const label = document.createElement('label');
            label.className = 'car-entry';
            label.innerHTML = `
                <span>${car.name}</span>
                <input type="number" step="0.01" data-car-id="${car.id}" placeholder="kWh" />
            `;
            container.appendChild(label);
        });
    }

    async function loadCars() {
        try {
            const cars = await fetchAPI('/cars/');
            renderCarInputs(cars);
            window.dispatchEvent(new CustomEvent('carsLoaded', { detail: cars }));
        } catch (error) {
            console.error('Kon auto\'s niet laden:', error);
            renderCarInputs([]);
            window.dispatchEvent(new CustomEvent('carsLoaded', { detail: [] }));
        }
    }

    function renderFinancialStatement(statement) {
        if (!statement) return;
        const formatter = new Intl.NumberFormat('nl-NL', { style: 'currency', currency: 'EUR' });
        const mappings = {
            'total-consumption': statement.total_consumption_cost_eur,
            'total-feed-in': statement.total_feed_in_revenue_eur,
            'net-energy': statement.net_energy_cost_eur,
            'car-reimbursement': statement.total_car_reimbursement_eur,
            'final-settlement': statement.final_settlement_eur
        };
        Object.entries(mappings).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value !== undefined && value !== null ? formatter.format(Number(value)) : '-';
            }
        });
        const details = document.getElementById('statement-details');
        if (details) {
            details.hidden = false;
        }
    }

    async function submitJournal(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const payload = {};

        formData.forEach((value, key) => {
            if (value === '') return;
            if (key === 'year' || key === 'month') {
                payload[key] = Number(value);
            } else {
                const numericValue = Number(value);
                payload[key] = Number.isNaN(numericValue) ? value : numericValue;
            }
        });

        const carEntries = [];
        form.querySelectorAll('[data-car-id]').forEach(input => {
            if (input.value === '') return;
            carEntries.push({
                car_id: Number(input.dataset.carId),
                total_charged_kwh: Number(input.value)
            });
        });
        payload.car_entries = carEntries;

        setFeedback('journal-feedback', 'Journaal wordt opgeslagen...', false);
        try {
            await fetchAPI('/journal/', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            setFeedback('journal-feedback', 'Journaal opgeslagen.', false);
            ensureYearOption(document.getElementById('statement-year'), payload.year);
            const statementMonth = document.getElementById('statement-month');
            if (statementMonth) {
                statementMonth.value = String(payload.month);
            }
            loadJournalStatement(payload.year, payload.month);
        } catch (error) {
            setFeedback('journal-feedback', error.message, true);
        }
    }

    async function loadJournalStatement(year, month) {
        const yearSelect = document.getElementById('statement-year');
        const monthSelect = document.getElementById('statement-month');
        const feedbackId = 'statement-feedback';
        const feedbackElement = document.getElementById(feedbackId);
        const selectedYear = year || (yearSelect ? Number(yearSelect.value) : undefined);
        const selectedMonth = month || (monthSelect ? Number(monthSelect.value) : undefined);

        if (!selectedYear || !selectedMonth) {
            setFeedback(feedbackId, 'Selecteer een jaar en maand.', true);
            return;
        }

        if (yearSelect) {
            ensureYearOption(yearSelect, selectedYear);
        }
        if (monthSelect) {
            monthSelect.value = String(selectedMonth);
        }

        setFeedback(feedbackId, 'Resultaten laden...', false);
        try {
            const data = await fetchAPI(`/journal/${selectedYear}/${selectedMonth}`);
            renderFinancialStatement(data.financial_statement);
            if (feedbackElement) {
                feedbackElement.textContent = `Resultaten voor ${monthNames[selectedMonth - 1]} ${selectedYear}`;
                feedbackElement.classList.remove('error');
                feedbackElement.classList.add('success');
            }
        } catch (error) {
            setFeedback(feedbackId, error.message, true);
            const details = document.getElementById('statement-details');
            if (details) {
                details.hidden = true;
            }
        }
    }

    function initializeSelectors() {
        const yearInput = document.getElementById('journal-year');
        const monthInput = document.getElementById('journal-month');
        const now = new Date();
        if (yearInput) {
            yearInput.value = now.getFullYear();
        }
        if (monthInput) {
            monthInput.value = String(now.getMonth() + 1);
        }
        populateYearSelect(document.getElementById('statement-year'));
        populateMonthSelect(document.getElementById('statement-month'));
    }

    function registerEventListeners() {
        const journalForm = document.getElementById('journal-form');
        if (journalForm) {
            journalForm.addEventListener('submit', submitJournal);
        }
        const loadStatementButton = document.getElementById('load-statement');
        if (loadStatementButton) {
            loadStatementButton.addEventListener('click', () => loadJournalStatement());
        }
        const logoutButton = document.getElementById('logout-button');
        if (logoutButton) {
            logoutButton.addEventListener('click', () => {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
            });
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        requireAuth();
        initializeSelectors();
        registerEventListeners();
        loadCars();
    });

    window.jouleJournal = {
        fetchAPI,
        loadCars,
        loadJournalStatement,
        submitJournal,
        requireAuth,
        ensureYearOption
    };
})();
