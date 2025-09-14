// --- Main Setup ---
document.addEventListener('DOMContentLoaded', () => {
    // Feather icons
    feather.replace();

    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Logout
    document.getElementById('logout-button').addEventListener('click', () => {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    });

    // Tab navigation
    const tabs = document.querySelectorAll('.tab-link');
    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            const targetTab = e.currentTarget.dataset.tab;
            document.querySelector('.tab-link.active').classList.remove('active');
            document.querySelector('.tab-content.active').classList.remove('active');
            e.currentTarget.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            loadDataForTab(targetTab);
        });
    });

    // Modal setup
    const modal = document.getElementById('form-modal');
    const closeBtn = document.querySelector('.close-btn');
    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    document.getElementById('modal-form').addEventListener('submit', handleFormSubmit);

    // Event listeners for "Add New" buttons
    document.querySelectorAll('.add-new-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const model = e.currentTarget.dataset.model;
            if (model) {
                openFormModal(model);
            }
        });
    });

    // Delegated event listeners for table actions
    document.querySelector('main').addEventListener('click', e => {
        const button = e.target.closest('.edit-btn, .delete-btn');
        if (button) {
            const model = button.dataset.model;
            const id = button.dataset.id;

            if (button.classList.contains('edit-btn')) {
                openFormModal(model, id);
            }
            if (button.classList.contains('delete-btn')) {
                handleDelete(model, id);
            }
        }
    });

    // Setup Journal Form
    const yearInput = document.getElementById('journal-year');
    const monthInput = document.getElementById('journal-month');
    if (yearInput && monthInput) {
        const now = new Date();
        yearInput.value = now.getFullYear();
        monthInput.value = now.getMonth() + 1;
        document.getElementById('journal-form').addEventListener('submit', handleJournalSubmit);
        loadCarsAndPopulateForm();
    }

    // Initial data load
    loadDataForTab('investments');

    // Debug buttons
    document.getElementById('clear-database-btn').addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear the entire database? This action cannot be undone.')) {
            try {
                await fetchAPI('/debug/clear-database', { method: 'POST' });
                alert('Database cleared successfully.');
                loadDataForTab('investments');
                loadDataForTab('tariffs');
            } catch (error) {
                console.error('Failed to clear database:', error);
                alert(`Error: ${error.message}`);
            }
        }
    });

    document.getElementById('fill-database-btn').addEventListener('click', async () => {
        if (confirm('Are you sure you want to fill the database with mockup data? This will overwrite existing data.')) {
            try {
                await fetchAPI('/debug/fill-database', { method: 'POST' });
                alert('Database filled with mockup data successfully.');
                loadDataForTab('investments');
                loadDataForTab('tariffs');
            } catch (error) {
                console.error('Failed to fill database:', error);
                alert(`Error: ${error.message}`);
            }
        }
    });
});


// --- API Helper ---
async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
    };
    const response = await fetch(`/api${endpoint}`, { ...options, headers });
    if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }
    if (!response.ok) {
        try {
            const errorData = await response.json();
            const errorMessage = typeof errorData.detail === 'string'
                ? errorData.detail
                : JSON.stringify(errorData.detail, null, 2);
            throw new Error(errorMessage || `API Error (${response.status})`);
        } catch (e) {
            throw new Error(`API Error (${response.status}): ${response.statusText}`);
        }
    }
    if (response.status === 204 || response.headers.get("content-length") === "0") {
        return null;
    }
    return response.json();
}


// --- Data Loading and Rendering ---
function loadDataForTab(tabName) {
    if (tabName === 'investments') {
        loadInvestmentsTab();
    } else if (tabName === 'tariffs') {
        loadGenericTab('tariffs');
    }
}

function loadGenericTab(modelNamePlural) {
    // Handle special case for solar_panel singular
    const modelName = modelNamePlural === 'solar_panels' ? 'solar_panel' : modelNamePlural.slice(0, -1);
    const config = MODEL_CONFIG[modelName];
    if (!config) return;

    const container = document.getElementById(`${modelNamePlural}-table-container`);
    if (!container) {
        console.error(`Container not found for ${modelNamePlural}`);
        return;
    }
    container.innerHTML = '<em>Loading...</em>';

    fetchAPI(`/${modelNamePlural}`)
        .then(data => {
            const table = createGenericTable(data, Object.keys(config.fields), modelName);
            container.innerHTML = '';
            container.appendChild(table);
        })
        .catch(error => {
            console.error(`Failed to load ${modelNamePlural}:`, error);
            container.innerHTML = `<p class="error-text">Error: ${error.message}</p>`;
        });
}

function createGenericTable(data, fields, modelName) {
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    const headerRow = document.createElement('tr');
    const displayFields = ['id', ...fields];
    displayFields.forEach(field => {
        const th = document.createElement('th');
        th.textContent = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        headerRow.appendChild(th);
    });
    headerRow.appendChild(document.createElement('th')).textContent = 'Actions';
    thead.appendChild(headerRow);

    if (data.length === 0) {
        const row = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = displayFields.length + 1;
        td.textContent = `No ${modelName.replace('_', ' ')}s found.`;
        row.appendChild(td);
        tbody.appendChild(row);
    } else {
        data.forEach(item => {
            const row = document.createElement('tr');
            displayFields.forEach(field => {
                const td = document.createElement('td');
                let value = item[field] === undefined || item[field] === null ? 'N/A' : item[field];
                if (field.includes('date') && value !== 'N/A') {
                    value = new Date(value).toLocaleDateString();
                }
                td.textContent = value;
                row.appendChild(td);
            });

            const tdActions = document.createElement('td');
            tdActions.innerHTML = `
                <button class="edit-btn" data-model="${modelName}" data-id="${item.id}"><i data-feather="edit-2" class="btn-icon"></i></button>
                <button class="delete-btn" data-model="${modelName}" data-id="${item.id}"><i data-feather="trash-2" class="btn-icon"></i></button>
            `;
            row.appendChild(tdActions);
            tbody.appendChild(row);
        });
    }

    table.appendChild(thead);
    table.appendChild(tbody);
    feather.replace();
    return table;
}


// --- Investments Tab Specific Logic ---
function loadInvestmentsTab() {
    loadGenericTab('solar_panels');
    loadGenericTab('batteries');
    loadGenericTab('cars');
}


// --- Model Configuration ---
const MODEL_CONFIG = {
    solar_panel: {
        title: 'Solar Panel',
        fields: {
            name: { label: 'Name', type: 'text', required: true, default: 'Zonnepanelen' },
            purchase_date: { label: 'Purchase Date', type: 'date', required: true },
            purchase_cost_eur: { label: 'Purchase Cost (€)', type: 'number', step: '0.01', required: true },
            total_power_wp: { label: 'Total Power (Wp)', type: 'number', required: true },
            expected_annual_yield_kwh: { label: 'Est. Annual Yield (kWh)', type: 'number' }
        }
    },
    battery: {
        title: 'Battery',
        fields: {
            name: { label: 'Name', type: 'text', required: true, default: 'Thuisbatterij' },
            brand: { label: 'Brand', type: 'text' },
            purchase_date: { label: 'Purchase Date', type: 'date', required: true },
            purchase_cost_eur: { label: 'Purchase Cost (€)', type: 'number', step: '0.01', required: true },
            capacity_kwh: { label: 'Capacity (kWh)', type: 'number', step: '0.1', required: true }
        }
    },
    car: {
        title: 'Car',
        fields: {
            name: { label: 'Name / License Plate', type: 'text', required: true },
            reimbursement_rate_eur_per_kwh: { label: 'Reimbursement Rate (€/kWh)', type: 'number', step: '0.001', required: true }
        }
    },
    tariff: {
        title: 'Tariff',
        fields: {
            start_date: { label: 'Start Date', type: 'date', required: true },
            end_date: { label: 'End Date', type: 'date' },
            purchase_low_eur_kwh: { label: 'Purchase Low (€/kWh)', type: 'number', step: '0.00001', required: true },
            purchase_high_eur_kwh: { label: 'Purchase High (€/kWh)', type: 'number', step: '0.00001', required: true },
            sale_eur_kwh: { label: 'Sale (€/kWh)', type: 'number', step: '0.00001', required: true },
            vat_percentage: { label: 'VAT (%)', type: 'number', step: '0.01', required: true },
        }
    },
};


// --- Modal Form Logic ---
function getPluralModelName(modelName) {
    if (modelName === 'battery') return 'batteries';
    if (modelName === 'solar_panel') return 'solar_panels';
    return `${modelName}s`;
}

async function openFormModal(modelName, id = null) {
    const config = MODEL_CONFIG[modelName];
    if (!config) {
        console.error("Unknown model type for form:", modelName);
        return;
    }
    const modal = document.getElementById('form-modal');
    const modalTitle = document.getElementById('modal-title');
    const form = document.getElementById('modal-form');

    form.innerHTML = '';
    form.dataset.model = modelName;
    form.dataset.id = id || '';

    let data = {};
    if (id) {
        modalTitle.textContent = `Edit ${config.title}`;
        try {
            const endpoint = `/${getPluralModelName(modelName)}/${id}`;
            data = await fetchAPI(endpoint);
        } catch (error) {
            console.error(`Failed to fetch ${modelName} data:`, error);
            alert(`Error: ${error.message}`);
            return;
        }
    } else {
        modalTitle.textContent = `Add New ${config.title}`;
    }

    for (const [key, fieldConfig] of Object.entries(config.fields)) {
        let value = data[key] || fieldConfig.default || '';
        const input = document.createElement('input');
        input.type = fieldConfig.type;
        input.name = key;
        input.id = `form-${key}`;
        if (input.type === 'date' && value) {
            input.value = value.split('T')[0];
        } else {
            input.value = value;
        }
        if (fieldConfig.step) input.step = fieldConfig.step;
        if (fieldConfig.required) input.required = true;

        const label = document.createElement('label');
        label.htmlFor = `form-${key}`;
        label.textContent = fieldConfig.label;

        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';
        formGroup.appendChild(label);
        formGroup.appendChild(input);
        form.appendChild(formGroup);
    }

    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.textContent = id ? 'Update' : 'Create';
    form.appendChild(submitButton);

    modal.style.display = 'block';
}

async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const modelName = form.dataset.model;
    const id = form.dataset.id;
    if (!modelName) return;

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const config = MODEL_CONFIG[modelName].fields;

    // Only set non-required fields to null if they are empty.
    // Let the backend handle validation for required fields.
    for (const key in data) {
        if (data[key] === '' && config[key] && !config[key].required) {
            data[key] = null;
        }
    }

    const endpoint = `/${getPluralModelName(modelName)}`;
    const method = id ? 'PUT' : 'POST';
    const finalEndpoint = id ? `${endpoint}/${id}` : endpoint;

    try {
        await fetchAPI(finalEndpoint, {
            method: method,
            body: JSON.stringify(data),
        });
        document.getElementById('form-modal').style.display = 'none';
        // Reload the correct tab
        if (modelName === 'tariff') {
            loadDataForTab('tariffs');
        } else {
            loadDataForTab('investments');
        }
    } catch (error) {
        console.error(`Failed to save ${modelName}:`, error);
        alert(`Error: ${error.message}`);
    }
}

// --- Journal Form Logic ---
async function loadCarsAndPopulateForm() {
    const container = document.getElementById('car-charging-entries');
    if (!container) return;
    try {
        const cars = await fetchAPI('/cars/');
        if (cars.length === 0) {
            container.innerHTML = '<p>No cars configured. Add one in the <a href="/admin">admin panel</a>.</p>';
            return;
        }
        container.innerHTML = ''; // Clear loading message
        cars.forEach(car => {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            formGroup.innerHTML = `
                <label for="car-${car.id}">${car.name}</label>
                <input type="number" step="0.01" name="car_charge_kwh" data-car-id="${car.id}">
            `;
            container.appendChild(formGroup);
        });
    } catch (error) {
        console.error('Failed to load cars:', error);
        container.innerHTML = `<p class="error-text">Could not load cars: ${error.message}</p>`;
    }
}

async function handleJournalSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const feedbackEl = document.getElementById('form-feedback');
    const submitBtn = form.querySelector('button[type="submit"]');

    submitBtn.textContent = 'Saving...';
    submitBtn.disabled = true;
    feedbackEl.textContent = '';
    feedbackEl.className = 'feedback-message';

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        if (key !== 'car_charge_kwh') {
            data[key] = value === '' ? null : Number(value);
        }
    });

    // Handle car entries separately
    data.car_entries = [];
    document.querySelectorAll('#car-charging-entries input').forEach(input => {
        if (input.value) {
            data.car_entries.push({
                car_id: Number(input.dataset.carId),
                total_charged_kwh: Number(input.value)
            });
        }
    });

    try {
        await fetchAPI('/journal/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
        feedbackEl.textContent = 'Journal saved successfully!';
        feedbackEl.classList.add('success');
        form.reset();
        // Optionally, reload metrics data if on the metrics tab
        if (document.getElementById('metrics').classList.contains('active')) {
            // You might need a function here to reload the metrics table
        }
    } catch (error) {
        console.error('Failed to save journal:', error);
        feedbackEl.textContent = `Error: ${error.message}`;
        feedbackEl.classList.add('error');
    } finally {
        submitBtn.textContent = 'Journaal Opslaan';
        submitBtn.disabled = false;
    }
}

async function handleDelete(modelName, id) {
    if (!confirm(`Are you sure you want to delete this ${modelName.replace('_', ' ')}? This action cannot be undone.`)) {
        return;
    }
    const endpoint = `/${getPluralModelName(modelName)}/${id}`;
    try {
        await fetchAPI(endpoint, { method: 'DELETE' });
        // Reload the correct tab
        if (modelName === 'tariff') {
            loadDataForTab('tariffs');
        } else {
            loadDataForTab('investments');
        }
    } catch (error) {
        console.error(`Failed to delete ${modelName}:`, error);
        alert(`Error: ${error.message}`);
    }
}
