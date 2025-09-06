// --- Main Setup ---
document.addEventListener('DOMContentLoaded', () => {
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
    const tabContents = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            document.querySelector('.tab-link.active').classList.remove('active');
            document.querySelector('.tab-content.active').classList.remove('active');
            tab.classList.add('active');
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
            openFormModal(e.target.dataset.model);
        });
    });

    // Delegated event listeners for table actions
    document.querySelector('main').addEventListener('click', e => {
        const button = e.target;
        const model = button.closest('.tab-content')?.id;
        if (!model) return;

        const id = button.dataset.id;
        if (button.classList.contains('edit-btn')) {
            openFormModal(model.slice(0, -1), id); // e.g., "investments" -> "investment"
        }
        if (button.classList.contains('delete-btn')) {
            handleDelete(model.slice(0, -1), id);
        }
    });

    // Initial data load
    loadDataForTab('investments');
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
        const errorData = await response.json();
        throw new Error(errorData.detail || `API Error (${response.status})`);
    }
    // For DELETE requests which might not have a body
    if (response.status === 204 || response.headers.get("content-length") === "0") {
        return null;
    }
    return response.json();
}


// --- Data Loading and Rendering ---
function loadDataForTab(tabName) {
    const modelName = tabName.slice(0, -1); // "investments" -> "investment"
    const config = MODEL_CONFIG[modelName];
    if (!config) return; // Not implemented yet

    const container = document.getElementById(`${tabName}-table-container`);
    container.innerHTML = '<em>Loading...</em>';

    fetchAPI(`/${tabName}`)
        .then(data => {
            if (data.length === 0) {
                container.innerHTML = `<p>No ${tabName} found. Add one to get started.</p>`;
                return;
            }
            const table = createTableFromData(data, Object.keys(config.fields), modelName);
            container.innerHTML = '';
            container.appendChild(table);
        })
        .catch(error => {
            console.error(`Failed to load ${tabName}:`, error);
            container.innerHTML = `<p class="error-text">Error: ${error.message}</p>`;
        });
}

function createTableFromData(data, fields, modelName) {
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    // Header
    const headerRow = document.createElement('tr');
    const displayFields = ['id', ...fields]; // Add id to the beginning
    displayFields.forEach(field => {
        const th = document.createElement('th');
        th.textContent = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        headerRow.appendChild(th);
    });
    headerRow.appendChild(document.createElement('th')).textContent = 'Actions';
    thead.appendChild(headerRow);

    // Body
    data.forEach(item => {
        const row = document.createElement('tr');
        displayFields.forEach(field => {
            const td = document.createElement('td');
            let value = item[field];
            if (typeof value === 'undefined' || value === null) {
                value = 'N/A';
            }
            // Simple truncation for long text
            if (typeof value === 'string' && value.length > 50) {
                td.textContent = value.substring(0, 50) + '...';
                td.title = value;
            } else {
                td.textContent = value;
            }
            row.appendChild(td);
        });

        const tdActions = document.createElement('td');
        tdActions.innerHTML = `
            <button class="edit-btn" data-id="${item.id}">Edit</button>
            <button class="delete-btn" data-id="${item.id}">Delete</button>
        `;
        row.appendChild(tdActions);
        tbody.appendChild(row);
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    return table;
}


// --- Model Configuration ---
const MODEL_CONFIG = {
    investment: {
        title: 'Investment',
        fields: {
            description: { label: 'Description', type: 'text', required: true },
            installation_date: { label: 'Installation Date', type: 'date', required: true },
            total_cost_eur: { label: 'Total Cost (€)', type: 'number', step: '0.01', required: true },
            total_power_wp: { label: 'Total Power (Wp)', type: 'number', required: true },
            estimated_annual_production_kwh: { label: 'Est. Annual Production (kWh)', type: 'number' }
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
            fixed_roi_rate_eur_kwh: { label: 'Fixed ROI Rate (€/kWh)', type: 'number', step: '0.00001' }
        }
    },
    metric: {
        title: 'Monthly Metric',
        fields: {
            period_start: { label: 'Period Start', type: 'date', required: true },
            account_name: { label: 'Account Name', type: 'text', required: true },
            production_total_kwh: { label: 'Production (kWh)', type: 'number', step: '0.01', required: true },
            import_low_kwh: { label: 'Import Low (kWh)', type: 'number', step: '0.01', required: true },
            import_high_kwh: { label: 'Import High (kWh)', type: 'number', step: '0.01', required: true },
            export_total_kwh: { label: 'Export (kWh)', type: 'number', step: '0.01', required: true },
            consumption_ev_kwh: { label: 'EV Consumption (kWh)', type: 'number', step: '0.01' },
            battery_charge_kwh: { label: 'Battery Charge (kWh)', type: 'number', step: '0.01' },
            battery_discharge_kwh: { label: 'Battery Discharge (kWh)', type: 'number', step: '0.01' },
            monthly_prepayment_eur: { label: 'Prepayment (€)', type: 'number', step: '0.01', required: true }
        }
    }
};


// --- Modal and Form Logic ---
async function openFormModal(modelName, id = null) {
    const config = MODEL_CONFIG[modelName];
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
            data = await fetchAPI(`/${modelName}s/${id}`);
        } catch (error) {
            console.error(`Failed to fetch ${modelName} data:`, error);
            alert(`Error: ${error.message}`);
            return;
        }
    } else {
        modalTitle.textContent = `Add New ${config.title}`;
    }

    for (const [key, fieldConfig] of Object.entries(config.fields)) {
        const value = data[key] || '';
        const input = document.createElement('input');
        input.type = fieldConfig.type;
        input.name = key;
        input.id = `form-${key}`;
        if (input.type === 'date' && value) {
            input.value = value.split('T')[0]; // Handle date formatting
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

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Clean up empty optional fields
    for (const key in data) {
        if (data[key] === '') {
            data[key] = null;
        }
    }

    try {
        if (id) {
            await fetchAPI(`/${modelName}s/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data),
            });
        } else {
            await fetchAPI(`/${modelName}s`, {
                method: 'POST',
                body: JSON.stringify(data),
            });
        }
        document.getElementById('form-modal').style.display = 'none';
        loadDataForTab(`${modelName}s`);
    } catch (error) {
        console.error(`Failed to save ${modelName}:`, error);
        alert(`Error: ${error.message}`);
    }
}

async function handleDelete(modelName, id) {
    if (!confirm(`Are you sure you want to delete this ${modelName}? This action cannot be undone.`)) {
        return;
    }
    try {
        await fetchAPI(`/${modelName}s/${id}`, { method: 'DELETE' });
        loadDataForTab(`${modelName}s`);
    } catch (error) {
        console.error(`Failed to delete ${modelName}:`, error);
        alert(`Error: ${error.message}`);
    }
}
