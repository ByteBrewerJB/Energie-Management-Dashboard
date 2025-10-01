// JouleJournal Dashboard - Main Application Logic

document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
    initDashboard();
});

// --- Globals ---
let energyBalanceChartInstance = null;
const monthNames = ["Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December"];

// --- Initialization ---
function initDashboard() {
    feather.replace();
    populatePeriodSelectors();
    setupEventListeners();
    loadLatestJournal();
    loadCars();
}

function setupEventListeners() {
    document.getElementById('load-journal-button').addEventListener('click', loadJournalStatement);
    document.getElementById('toggle-journal-form').addEventListener('click', toggleJournalForm);
    document.getElementById('journal-form').addEventListener('submit', submitJournal);
    document.getElementById('cancel-journal-form').addEventListener('click', () => toggleJournalForm(false));
}

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
        throw new Error('Niet geautoriseerd (sessie verlopen)');
    }
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Onbekende serverfout.' }));
        const errorMessage = typeof errorData.detail === 'string'
            ? errorData.detail
            : JSON.stringify(errorData.detail, null, 2);
        throw new Error(errorMessage || `API Fout (${response.status})`);
    }
    if (response.status === 204 || response.headers.get("content-length") === "0") {
        return null;
    }
    return response.json();
}


// --- Period & Data Loading ---
function populatePeriodSelectors(selectedYear, selectedMonth) {
    const yearSelector = document.getElementById('year-selector');
    const monthSelector = document.getElementById('month-selector');
    const currentYear = new Date().getFullYear();

    // Clear existing options
    yearSelector.innerHTML = '';
    monthSelector.innerHTML = '';

    // Populate years (e.g., last 5 years up to current)
    for (let i = 0; i < 5; i++) {
        const year = currentYear - i;
        const option = new Option(year, year);
        yearSelector.add(option);
    }
    yearSelector.value = selectedYear || currentYear;

    // Populate months
    monthNames.forEach((name, index) => {
        const option = new Option(name, index + 1);
        monthSelector.add(option);
    });
    monthSelector.value = selectedMonth || (new Date().getMonth() + 1);
}

async function loadLatestJournal() {
    const year = new Date().getFullYear();
    try {
        // This endpoint returns all journals for the year, sorted by month descending
        const journals = await fetchAPI(`/journal/${year}`);
        if (journals && journals.length > 0) {
            const latestJournal = journals[0]; // The first one is the most recent
            const { year, month } = latestJournal.metric;
            populatePeriodSelectors(year, month); // Update selectors to match loaded data
            renderDashboard(latestJournal);
        } else {
            // No data for current year, check previous year
            const prevYearJournals = await fetchAPI(`/journal/${year - 1}`);
             if (prevYearJournals && prevYearJournals.length > 0) {
                const latestJournal = prevYearJournals[0];
                const { year, month } = latestJournal.metric;
                populatePeriodSelectors(year, month);
                renderDashboard(latestJournal);
             } else {
                showPlaceholder("Geen recente journaalgegevens gevonden. Selecteer een periode of voer een nieuw journaal in.");
             }
        }
    } catch (error) {
        showError("Fout bij het laden van het laatste journaal: " + error.message);
    }
}

async function loadJournalStatement() {
    const year = document.getElementById('year-selector').value;
    const month = document.getElementById('month-selector').value;

    showPlaceholder("Dashboardgegevens laden...");

    try {
        const data = await fetchAPI(`/journal/${year}/${month}`);
        renderDashboard(data);
    } catch (error) {
        showError(`Kon journaal voor ${monthNames[month-1]} ${year} niet laden: ${error.message}`);
    }
}

// --- UI Rendering ---
function renderDashboard(data) {
    document.getElementById('results-section').style.display = 'block';
    document.getElementById('roi-card').style.display = 'block'; // Ensure ROI card is visible
    document.querySelector('.chart-grid').style.display = 'grid';

    renderKPIs(data);
    renderFinancialStatement(data.financial_statement);
    renderEnergyBalanceChart(data);

    // Placeholder for ROI data loading
    // renderRoiTracker(roiData);
}

function renderKPIs(data) {
    const kpisDiv = document.getElementById('kpis');
    const { metric, energy_flow, financial_statement } = data;
    const kpiTitle = document.getElementById('kpi-title');
    kpiTitle.innerHTML = `<i data-feather="bar-chart-2"></i> Kerncijfers (${monthNames[metric.month-1]} ${metric.year})`;

    kpisDiv.innerHTML = `
        <div class="kpi-item">
            <h3>Netto Saldo</h3>
            <p>€ ${parseFloat(financial_statement.final_settlement_eur).toFixed(2)}</p>
        </div>
        <div class="kpi-item">
            <h3>Zelfvoorzienendheid</h3>
            <p>${(parseFloat(energy_flow.self_sufficiency_ratio) * 100).toFixed(1)} %</p>
        </div>
        <div class="kpi-item">
            <h3>Zonproductie</h3>
            <p>${parseFloat(metric.solar_production_kwh).toFixed(0)} kWh</p>
        </div>
        <div class="kpi-item">
            <h3>Netto Verbruik</h3>
            <p>${(parseFloat(energy_flow.import_total_kwh) - parseFloat(energy_flow.total_grid_feed_in_kwh)).toFixed(0)} kWh</p>
        </div>
    `;
    feather.replace();
}

function renderFinancialStatement(statement) {
    const container = document.getElementById('financial-statement');
    container.innerHTML = `
        <div class="kpi-item">
            <label>Verbruikskosten</label>
            <span>€ ${parseFloat(statement.total_consumption_cost_eur).toFixed(2)}</span>
        </div>
        <div class="kpi-item">
            <label>Terugleveropbrengst</label>
            <span>€ ${parseFloat(statement.total_feed_in_revenue_eur).toFixed(2)}</span>
        </div>
         <div class="kpi-item">
            <label>Netto Energiekosten</label>
            <span>€ ${parseFloat(statement.net_energy_cost_eur).toFixed(2)}</span>
        </div>
        <div class="kpi-item">
            <label>Voorschot</label>
            <span>€ ${parseFloat(statement.monthly_prepayment_eur).toFixed(2)}</span>
        </div>
        <div class="kpi-item">
            <label>Autovergoeding</label>
            <span>€ ${parseFloat(statement.total_car_reimbursement_eur).toFixed(2)}</span>
        </div>
        <div class="kpi-item final-settlement">
            <label>Eindafrekening</label>
            <span>€ ${parseFloat(statement.final_settlement_eur).toFixed(2)}</span>
        </div>
    `;
}


function renderEnergyBalanceChart(data) {
    const ctx = document.getElementById('energyBalanceChart').getContext('2d');
    if (!ctx) return;

    const { energy_flow } = data;
    const labels = [monthNames[data.metric.month-1]];
    const datasets = [
        { label: 'Import (kWh)', data: [energy_flow.import_total_kwh], backgroundColor: '#FF6384' },
        { label: 'Zelfverbruik (kWh)', data: [energy_flow.self_consumption_kwh], backgroundColor: '#36A2EB' },
        { label: 'Export (kWh)', data: [energy_flow.total_grid_feed_in_kwh], backgroundColor: '#FFCE56' }
    ];

    if (energyBalanceChartInstance) {
        energyBalanceChartInstance.destroy();
    }
    energyBalanceChartInstance = new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Energiebalans' },
                tooltip: { mode: 'index', intersect: false },
            },
            scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true, title: { display: true, text: 'kWh' } } }
        }
    });
}

function showPlaceholder(message) {
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('roi-card').style.display = 'none';
    document.querySelector('.chart-grid').style.display = 'none';

    const kpiContainer = document.getElementById('kpis');
    kpiContainer.innerHTML = `<p>${message}</p>`;
    // Make sure the parent is visible
    document.getElementById('kpi-card').style.display = 'block';
    document.getElementById('kpi-title').innerText = "Dashboard";
}

function showError(message) {
    const kpiContainer = document.getElementById('kpis');
    kpiContainer.innerHTML = `<div class="error-message"><strong>Fout:</strong><p>${message}</p></div>`;
     document.getElementById('kpi-card').style.display = 'block';
    document.getElementById('kpi-title').innerText = "Fout";
}

// --- Form Handling ---
function toggleJournalForm(show) {
    const container = document.getElementById('journal-form-container');
    if (show === undefined) {
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
    } else {
        container.style.display = show ? 'block' : 'none';
    }

    if (container.style.display === 'block') {
        const now = new Date();
        document.getElementById('journal-year').value = now.getFullYear();
        document.getElementById('journal-month').value = now.getMonth() + 1;
    }
}

async function loadCars() {
    try {
        const cars = await fetchAPI('/cars/');
        const container = document.getElementById('car-charging-section');

        // Clear previous entries
        const existingEntries = container.querySelectorAll('.form-row');
        existingEntries.forEach(entry => entry.remove());

        if (cars && cars.length > 0) {
            cars.forEach(car => {
                const carRow = document.createElement('div');
                carRow.className = 'form-row';
                carRow.innerHTML = `
                    <div class="form-group">
                        <label for="car_kwh_${car.id}">${car.name}</label>
                        <input type="number" step="0.01" id="car_kwh_${car.id}" name="total_charged_kwh" data-car-id="${car.id}" class="form-control">
                    </div>
                `;
                container.appendChild(carRow);
            });
        } else {
            container.innerHTML += '<p>Geen auto\'s geconfigureerd. Voeg een auto toe in het <a href="/admin">admin paneel</a>.</p>';
        }
    } catch (error) {
        console.error("Kon auto's niet laden:", error);
    }
}

async function submitJournal(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const json = {};

    // Convert FormData to simple JSON
    formData.forEach((value, key) => {
        if (value) { // Only include non-empty values
            json[key] = parseFloat(value) || value;
        }
    });

    // Handle car entries
    json.car_entries = [];
    const carInputs = form.querySelectorAll('[data-car-id]');
    carInputs.forEach(input => {
        if (input.value) {
            json.car_entries.push({
                car_id: parseInt(input.dataset.carId, 10),
                total_charged_kwh: parseFloat(input.value)
            });
        }
    });

    try {
        await fetchAPI('/journal/', {
            method: 'POST',
            body: JSON.stringify(json),
        });
        toggleJournalForm(false);
        // Reload the data for the period we just submitted
        populatePeriodSelectors(json.year, json.month);
        loadJournalStatement();
        alert('Journaal succesvol opgeslagen!');
    } catch (error) {
        alert(`Fout bij opslaan journaal: ${error.message}`);
    }
}
