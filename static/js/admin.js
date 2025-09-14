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
        // Specific handler for Journal Edit buttons MUST come first
        const journalEditBtn = e.target.closest('.journal-edit-btn');
        if (journalEditBtn) {
            const journalData = JSON.parse(journalEditBtn.dataset.journal);
            populateJournalForm(journalData);
            return; // Stop further processing
        }

        // Generic handler for other edit/delete buttons
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
    const metricYearSelector = document.getElementById('metric-year-selector');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');

    if (yearInput && monthInput) {
        const now = new Date();
        const currentYear = now.getFullYear();

        // Populate year selector for metrics tab
        if (metricYearSelector) {
            for (let i = currentYear + 1; i >= currentYear - 5; i--) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i;
                metricYearSelector.appendChild(option);
            }
            metricYearSelector.value = currentYear; // Set default value
        }

        yearInput.value = currentYear;
        monthInput.value = now.getMonth() + 1;
        document.getElementById('journal-form').addEventListener('submit', handleJournalSubmit);
        loadCarsAndPopulateForm();

        // Add event listener for year change
        if (metricYearSelector) {
            metricYearSelector.addEventListener('change', () => {
                if (document.getElementById('metrics').classList.contains('active')) {
                    loadAndDisplayJournals(metricYearSelector.value);
                }
            });
        }

        // Add event listener for the cancel button
        if (cancelEditBtn) {
            cancelEditBtn.addEventListener('click', () => {
                resetJournalForm();
            });
        }
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
    } else if (tabName === 'metrics') {
        const selectedYear = document.getElementById('metric-year-selector').value;
        if (selectedYear) {
            loadAndDisplayJournals(selectedYear);
        }
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

async function loadAndDisplayJournals(year) {
    const container = document.getElementById('metrics-table-container');
    container.innerHTML = '<em>Loading journals...</em>';

    try {
        const journals = await fetchAPI(`/journal/${year}`);
        if (!journals || journals.length === 0) {
            container.innerHTML = `<p>No journal entries found for ${year}.</p>`;
            return;
        }
        const table = createJournalTable(journals);
        container.innerHTML = '';
        container.appendChild(table);
    } catch (error) {
        console.error(`Failed to load journals for year ${year}:`, error);
        container.innerHTML = `<p class="error-text">Error loading journals: ${error.message}</p>`;
    }
}

function createJournalTable(journals) {
    const table = document.createElement('table');
    table.className = 'data-table'; // Use existing class for styling
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    const headerRow = document.createElement('tr');
    ['Year', 'Month', 'Actions'].forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Sort journals by month descending before creating rows
    journals.sort((a, b) => b.metric.month - a.metric.month);

    journals.forEach(journalData => {
        const row = document.createElement('tr');
        // The raw journal data is in the 'metric' property
        const journal = journalData.metric;

        const yearCell = document.createElement('td');
        yearCell.textContent = journal.year;
        row.appendChild(yearCell);

        const monthCell = document.createElement('td');
        // Convert month number to name
        const monthName = new Date(journal.year, journal.month - 1).toLocaleString('nl-NL', { month: 'long' });
        monthCell.textContent = monthName.charAt(0).toUpperCase() + monthName.slice(1);
        row.appendChild(monthCell);

        const actionsCell = document.createElement('td');
        actionsCell.className = 'actions-cell';
        const editButton = document.createElement('button');
        editButton.innerHTML = '<i data-feather="edit-2" class="btn-icon"></i> Bewerken';
        editButton.className = 'journal-edit-btn';
        editButton.title = `Edit journal for ${monthName} ${journal.year}`;

        // Store the full data object on the button. This is simpler for the next step.
        editButton.dataset.journal = JSON.stringify(journalData);
        actionsCell.appendChild(editButton);
        row.appendChild(actionsCell);

        tbody.appendChild(row);
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    feather.replace(); // To render the new icons
    return table;
}

function populateJournalForm(journalData) {
    const form = document.getElementById('journal-form');
    const journal = journalData.metric; // The core data

    // Reset form to clear any previous state or validation
    form.reset();

    // Set form to "edit mode" and store identifiers
    form.dataset.editingYear = journal.year;
    form.dataset.editingMonth = journal.month;

    // Update form title
    const titleElement = document.querySelector('#journal-entry-card h2');
    if (titleElement) {
        const monthName = new Date(journal.year, journal.month - 1).toLocaleString('nl-NL', { month: 'long' });
        titleElement.innerHTML = `<i data-feather="edit"></i> Journaal Bewerken voor ${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${journal.year}`;
        feather.replace();
    }

    // Populate all fields from the journal object
    for (const key in journal) {
        if (Object.prototype.hasOwnProperty.call(journal, key)) {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = journal[key];
            }
        }
    }

    // Populate car entries
    if (journal.car_entries && journal.car_entries.length > 0) {
        journal.car_entries.forEach(entry => {
            const carInput = form.querySelector(`input[data-car-id="${entry.car_id}"]`);
            if (carInput) {
                carInput.value = entry.total_charged_kwh;
            }
        });
    }

    // Show cancel button
    document.getElementById('cancel-edit-btn').classList.remove('hidden');

    // Scroll to the form to make it visible
    form.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function resetJournalForm() {
    const form = document.getElementById('journal-form');
    form.reset();

    // Remove editing state
    delete form.dataset.editingYear;
    delete form.dataset.editingMonth;

    // Reset title
    const titleElement = document.querySelector('#journal-entry-card h2');
    if (titleElement) {
        titleElement.innerHTML = `<i data-feather="edit"></i> Maandjournaal Invoeren`;
        feather.replace();
    }

    // Reset year and month dropdowns to current
    const now = new Date();
    const yearInput = document.getElementById('journal-year');
    const monthInput = document.getElementById('journal-month');
    if (yearInput) yearInput.value = now.getFullYear();
    if (monthInput) monthInput.value = now.getMonth() + 1;

    // Clear feedback message
    const feedbackEl = document.getElementById('form-feedback');
    if(feedbackEl) {
        feedbackEl.textContent = '';
        feedbackEl.className = 'feedback-message';
    }

    // Hide cancel button
    document.getElementById('cancel-edit-btn').classList.add('hidden');
}


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
            // For number fields, convert empty string to null instead of 0
            const input = form.querySelector(`[name="${key}"]`);
            if (input && input.type === 'number') {
                data[key] = value === '' ? null : Number(value);
            } else {
                data[key] = value;
            }
        }
    });
    // Year and month are required, ensure they are numbers
    data.year = Number(formData.get('year'));
    data.month = Number(formData.get('month'));


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

    const isEditing = !!form.dataset.editingYear;
    const method = isEditing ? 'PUT' : 'POST';
    const yearToUpdate = isEditing ? form.dataset.editingYear : data.year;
    const monthToUpdate = isEditing ? form.dataset.editingMonth : data.month;
    const endpoint = isEditing ? `/journal/${yearToUpdate}/${monthToUpdate}` : '/journal/';

    try {
        await fetchAPI(endpoint, {
            method: method,
            body: JSON.stringify(data),
        });

        feedbackEl.textContent = `Journal for ${data.year}-${data.month} saved successfully!`;
        feedbackEl.classList.add('success');

        resetJournalForm();

        // Reload the journal table to show the new data
        const selectedYear = document.getElementById('metric-year-selector').value;
        loadAndDisplayJournals(selectedYear);

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
