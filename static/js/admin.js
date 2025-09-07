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

    // Modal setup for non-metric forms
    const modal = document.getElementById('form-modal');
    const closeBtn = document.querySelector('.close-btn');
    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    document.getElementById('modal-form').addEventListener('submit', handleFormSubmit);

    // Event listeners for "Add New" buttons (non-metric)
    document.querySelectorAll('.add-new-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            openFormModal(e.target.dataset.model);
        });
    });

    // Delegated event listeners for table actions (non-metric)
    document.querySelector('main').addEventListener('click', e => {
        if (e.target.matches('.edit-btn, .delete-btn')) {
            const button = e.target;
            const model = button.closest('.tab-content')?.id;
            if (!model || model === 'metrics') return;

            const id = button.dataset.id;
            if (button.classList.contains('edit-btn')) {
                openFormModal(model.slice(0, -1), id);
            }
            if (button.classList.contains('delete-btn')) {
                handleDelete(model.slice(0, -1), id);
            }
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


// --- Generic Data Loading and Rendering (for Investments, Tariffs) ---
function loadDataForTab(tabName) {
    if (tabName === 'metrics') {
        loadMetricsTab();
        return;
    }

    const modelName = tabName.slice(0, -1);
    const config = MODEL_CONFIG[modelName];
    if (!config) return;

    const container = document.getElementById(`${tabName}-table-container`);
    container.innerHTML = '<em>Loading...</em>';

    fetchAPI(`/${tabName}`)
        .then(data => {
            if (data.length === 0) {
                container.innerHTML = `<p>No ${tabName} found. Add one to get started.</p>`;
                return;
            }
            const table = createGenericTable(data, Object.keys(config.fields), modelName);
            container.innerHTML = '';
            container.appendChild(table);
        })
        .catch(error => {
            console.error(`Failed to load ${tabName}:`, error);
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

    data.forEach(item => {
        const row = document.createElement('tr');
        displayFields.forEach(field => {
            const td = document.createElement('td');
            let value = item[field] === undefined || item[field] === null ? 'N/A' : item[field];
            td.textContent = value;
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
            grid_consumption_low_kwh: { label: 'Grid Cons. Low (kWh)', type: 'number', step: '0.01' },
            grid_consumption_high_kwh: { label: 'Grid Cons. High (kWh)', type: 'number', step: '0.01' },
            grid_feed_in_low_kwh: { label: 'Grid Feed-in Low (kWh)', type: 'number', step: '0.01' },
            grid_feed_in_high_kwh: { label: 'Grid Feed-in High (kWh)', type: 'number', step: '0.01' },
            consumption_price_low_eur_kwh: { label: 'Cons. Price Low (€/kWh)', type: 'number', step: '0.00001' },
            consumption_price_high_eur_kwh: { label: 'Cons. Price High (€/kWh)', type: 'number', step: '0.00001' },
            feed_in_tariff_low_eur_kwh: { label: 'Feed-in Low (€/kWh)', type: 'number', step: '0.00001' },
            feed_in_tariff_high_eur_kwh: { label: 'Feed-in High (€/kWh)', type: 'number', step: '0.00001' },
            solar_production_kwh: { label: 'Solar Prod. (kWh)', type: 'number', step: '0.01' },
            battery_charge_kwh: { label: 'Battery Charge (kWh)', type: 'number', step: '0.01' },
            battery_discharge_kwh: { label: 'Battery Discharge (kWh)', type: 'number', step: '0.01' },
            monthly_prepayment_eur: { label: 'Prepayment (€)', type: 'number', step: '0.01' },
        }
    }
};


// --- Metrics Tab Specific Logic ---
function loadMetricsTab() {
    const yearSelector = document.getElementById('metric-year-selector');
    const currentYear = new Date().getFullYear();

    // Populate year selector
    yearSelector.innerHTML = '';
    for (let i = currentYear + 1; i >= currentYear - 10; i--) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        if (i === currentYear) {
            option.selected = true;
        }
        yearSelector.appendChild(option);
    }

    yearSelector.addEventListener('change', () => {
        renderMetricsTable(yearSelector.value);
    });

    renderMetricsTable(currentYear);
}

async function renderMetricsTable(year) {
    const container = document.getElementById('metrics-table-container');
    container.innerHTML = '<em>Loading...</em>';

    try {
        const data = await fetchAPI(`/metrics/${year}`);
        const table = document.createElement('table');
        table.className = 'editable-table';
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');
        const fields = MODEL_CONFIG.metric.fields;

        // Header
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = '<th>Month</th>';
        for (const key in fields) {
            headerRow.innerHTML += `<th>${fields[key].label}</th>`;
        }
        headerRow.innerHTML += '<th>Actions</th>';
        thead.appendChild(headerRow);

        // Body
        data.forEach(item => {
            const row = document.createElement('tr');
            row.dataset.month = item.month;
            const monthName = new Date(year, item.month - 1, 1).toLocaleString('default', { month: 'long' });
            row.innerHTML = `<td>${monthName}</td>`;

            let isComplete = true;
            for (const key in fields) {
                const value = item[key] === null ? '' : item[key];
                if (value === '') isComplete = false;
                const fieldConfig = fields[key];
                row.innerHTML += `
                    <td>
                        <input
                            type="${fieldConfig.type}"
                            name="${key}"
                            value="${value}"
                            step="${fieldConfig.step || ''}"
                            class="editable-input"
                        />
                    </td>
                `;
            }
            row.innerHTML += `
                <td>
                    <button class="save-metric-btn">Save</button>
                </td>
            `;
            tbody.appendChild(row);
            row.classList.toggle('incomplete', !isComplete);
            row.classList.toggle('complete', isComplete);
        });

        table.appendChild(thead);
        table.appendChild(tbody);
        container.innerHTML = '';
        container.appendChild(table);

        // Add event listeners for save buttons
        table.querySelectorAll('.save-metric-btn').forEach(btn => {
            btn.addEventListener('click', handleMetricSave);
        });

    } catch (error) {
        console.error(`Failed to load metrics for ${year}:`, error);
        container.innerHTML = `<p class="error-text">Error: ${error.message}</p>`;
    }
}

async function handleMetricSave(event) {
    const button = event.target;
    const row = button.closest('tr');
    const year = document.getElementById('metric-year-selector').value;
    const month = row.dataset.month;

    const data = {};
    const inputs = row.querySelectorAll('input.editable-input');
    let isComplete = true;

    inputs.forEach(input => {
        const value = input.value;
        if (value === '') {
            data[input.name] = null;
            isComplete = false;
        } else {
            data[input.name] = Number(value);
        }
    });

    button.textContent = 'Saving...';
    button.disabled = true;

    try {
        await fetchAPI(`/metrics/${year}/${month}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
        button.textContent = 'Save';
        button.disabled = false;
        row.classList.remove('incomplete', 'complete');
        row.classList.add(isComplete ? 'complete' : 'incomplete');
        // Optional: Add a temporary success indicator
        row.classList.add('success-flash');
        setTimeout(() => row.classList.remove('success-flash'), 1500);

    } catch (error) {
        console.error('Failed to save metric:', error);
        alert(`Error: ${error.message}`);
        button.textContent = 'Save';
        button.disabled = false;
    }
}


// --- Generic Modal Form Logic (for Investments, Tariffs) ---
// This part remains unchanged for other tabs.
async function openFormModal(modelName, id = null) { /* ... existing implementation ... */ }
async function handleFormSubmit(event) { /* ... existing implementation ... */ }
async function handleDelete(modelName, id) { /* ... existing implementation ... */ }
// NOTE: I'm replacing the file, so I need to include the full content of the functions I'm keeping.
// I will copy the content of the old functions here.

async function openFormModal(modelName, id = null) {
    const config = MODEL_CONFIG[modelName];
    if (!config) return; // Should not happen for investments/tariffs
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
            // Note: The generic API endpoint is pluralized
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
