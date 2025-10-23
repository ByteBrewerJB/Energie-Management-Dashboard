(function () {
    const { requireAuth, fetchAPI, loadCars } = window.jouleJournal;

    async function loadSingleInstallation(endpoint, formId, feedbackId, fieldMap) {
        try {
            const data = await fetchAPI(endpoint);
            const form = document.getElementById(formId);
            if (!form) return;
            if (Array.isArray(data) && data.length > 0) {
                const record = data[0];
                form.dataset.recordId = record.id;
                Object.entries(fieldMap).forEach(([fieldName, accessor]) => {
                    const input = form.querySelector(`[name="${fieldName}"]`);
                    if (!input) return;
                    let value = typeof accessor === 'function' ? accessor(record) : record[fieldName];
                    if (value === null || value === undefined) {
                        value = '';
                    }
                    input.value = value;
                });
                setFeedback(feedbackId, 'Gegevens geladen.', false);
            } else {
                delete form.dataset.recordId;
                form.reset();
                setFeedback(feedbackId, 'Nog geen gegevens opgeslagen.', false);
            }
        } catch (error) {
            setFeedback(feedbackId, error.message, true);
        }
    }

    function collectFormValues(form) {
        const data = {};
        const formData = new FormData(form);
        formData.forEach((value, key) => {
            if (value === '') {
                data[key] = null;
                return;
            }
            if (key.includes('date')) {
                data[key] = value;
            } else {
                const numeric = Number(value);
                data[key] = Number.isNaN(numeric) ? value : numeric;
            }
        });
        return data;
    }

    function setFeedback(elementId, message, isError) {
        const element = document.getElementById(elementId);
        if (!element) return;
        element.textContent = message;
        element.classList.toggle('error', Boolean(message) && isError);
        element.classList.toggle('success', Boolean(message) && !isError);
    }

    async function handleInstallationSubmit(event, config) {
        event.preventDefault();
        const form = event.target;
        const payload = collectFormValues(form);
        const recordId = form.dataset.recordId;
        setFeedback(config.feedbackId, 'Opslaan...', false);
        try {
            const method = recordId ? 'PUT' : 'POST';
            const endpoint = recordId ? `${config.endpoint}/${recordId}` : config.endpoint;
            await fetchAPI(endpoint, {
                method,
                body: JSON.stringify(payload)
            });
            setFeedback(config.feedbackId, 'Gegevens opgeslagen.', false);
            loadSingleInstallation(config.endpoint, config.formId, config.feedbackId, config.fieldMap);
        } catch (error) {
            setFeedback(config.feedbackId, error.message, true);
        }
    }

    async function handleCarSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const payload = collectFormValues(form);
        setFeedback('car-feedback', 'Auto wordt toegevoegd...', false);
        try {
            await fetchAPI('/cars', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            form.reset();
            setFeedback('car-feedback', 'Auto toegevoegd.', false);
            loadCars();
        } catch (error) {
            setFeedback('car-feedback', error.message, true);
        }
    }

    async function handleCarDelete(carId) {
        if (!confirm('Weet je zeker dat je deze auto wilt verwijderen?')) {
            return;
        }
        try {
            await fetchAPI(`/cars/${carId}`, { method: 'DELETE' });
            loadCars();
        } catch (error) {
            alert(`Verwijderen mislukt: ${error.message}`);
        }
    }

    function renderCarTable(cars) {
        const tbody = document.getElementById('car-table-body');
        if (!tbody) return;
        tbody.innerHTML = '';
        if (!cars.length) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 3;
            cell.textContent = 'Geen auto\'s beschikbaar.';
            row.appendChild(cell);
            tbody.appendChild(row);
            return;
        }
        cars.forEach(car => {
            const row = document.createElement('tr');
            const nameCell = document.createElement('td');
            nameCell.textContent = car.name;
            const rateCell = document.createElement('td');
            rateCell.textContent = Number(car.reimbursement_rate_eur_per_kwh).toFixed(4);
            const actionCell = document.createElement('td');
            const deleteButton = document.createElement('button');
            deleteButton.className = 'btn-danger';
            deleteButton.textContent = 'Verwijderen';
            deleteButton.dataset.action = 'delete';
            deleteButton.dataset.carId = car.id;
            actionCell.appendChild(deleteButton);
            row.appendChild(nameCell);
            row.appendChild(rateCell);
            row.appendChild(actionCell);
            tbody.appendChild(row);
        });
    }

    function registerEventListeners() {
        const solarPanelForm = document.getElementById('solar-panel-form');
        if (solarPanelForm) {
            solarPanelForm.addEventListener('submit', event => handleInstallationSubmit(event, {
                endpoint: '/solar_panels',
                formId: 'solar-panel-form',
                feedbackId: 'solar-panel-feedback',
                fieldMap: {
                    name: 'name',
                    purchase_date: record => (record.purchase_date ? record.purchase_date.slice(0, 10) : ''),
                    purchase_cost_eur: 'purchase_cost_eur',
                    total_power_wp: 'total_power_wp'
                }
            }));
        }

        const batteryForm = document.getElementById('battery-form');
        if (batteryForm) {
            batteryForm.addEventListener('submit', event => handleInstallationSubmit(event, {
                endpoint: '/batteries',
                formId: 'battery-form',
                feedbackId: 'battery-feedback',
                fieldMap: {
                    name: 'name',
                    purchase_date: record => (record.purchase_date ? record.purchase_date.slice(0, 10) : ''),
                    purchase_cost_eur: 'purchase_cost_eur',
                    capacity_kwh: 'capacity_kwh'
                }
            }));
        }

        const carForm = document.getElementById('car-form');
        if (carForm) {
            carForm.addEventListener('submit', handleCarSubmit);
        }

        const carTable = document.getElementById('car-table-body');
        if (carTable) {
            carTable.addEventListener('click', event => {
                const button = event.target.closest('button[data-action="delete"]');
                if (!button) return;
                const carId = Number(button.dataset.carId);
                if (!Number.isNaN(carId)) {
                    handleCarDelete(carId);
                }
            });
        }

        const logoutButton = document.getElementById('logout-button');
        if (logoutButton) {
            logoutButton.addEventListener('click', () => {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
            });
        }

        window.addEventListener('carsLoaded', event => renderCarTable(event.detail || []));
    }

    document.addEventListener('DOMContentLoaded', () => {
        requireAuth();
        registerEventListeners();
        loadSingleInstallation('/solar_panels', 'solar-panel-form', 'solar-panel-feedback', {
            name: 'name',
            purchase_date: record => (record.purchase_date ? record.purchase_date.slice(0, 10) : ''),
            purchase_cost_eur: 'purchase_cost_eur',
            total_power_wp: 'total_power_wp'
        });
        loadSingleInstallation('/batteries', 'battery-form', 'battery-feedback', {
            name: 'name',
            purchase_date: record => (record.purchase_date ? record.purchase_date.slice(0, 10) : ''),
            purchase_cost_eur: 'purchase_cost_eur',
            capacity_kwh: 'capacity_kwh'
        });
        loadCars();
    });
})();
