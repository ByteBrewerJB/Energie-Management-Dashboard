// Energie Management Dashboard - Main Application Logic

// Store chart instances to destroy them before re-rendering
let energyBalanceChartInstance = null;
let consumptionSplitChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard Initialized.');

    // --- EVENT LISTENERS ---
    const dateForm = document.getElementById('date-range-form');
    if (dateForm) {
        dateForm.addEventListener('submit', handleAnalysisFormSubmit);
    }

    const metricForm = document.getElementById('metric-form');
    if (metricForm) {
        metricForm.addEventListener('submit', handleMetricFormSubmit);
    }

    // --- INITIAL DATA LOAD ---
    // Set default dates to the last 3 months and load data
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 3);

    const startDateString = startDate.toISOString().split('T')[0];
    const endDateString = endDate.toISOString().split('T')[0];

    document.getElementById('start-date').value = startDateString;
    document.getElementById('end-date').value = endDateString;

    loadDashboard(startDateString, endDateString);
});

async function handleAnalysisFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const startDate = form.elements.start_date.value;
    const endDate = form.elements.end_date.value;
    await loadDashboard(startDate, endDate);
}

async function loadDashboard(startDate, endDate) {
    console.log(`Loading dashboard for ${startDate} to ${endDate}`);
    const kpisDiv = document.getElementById('kpis');
    kpisDiv.innerHTML = '<em>Loading analysis...</em>';

    try {
        const response = await fetch(`/api/v1/analysis?start_date=${startDate}&end_date=${endDate}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch analysis data.');
        }
        const data = await response.json();

        renderKPIs(data.monthly_data);
        renderRoiTracker(data.roi);
        renderEnergyBalanceChart(data.monthly_data);
        renderConsumptionSplitChart(data.monthly_data);

    } catch (error) {
        console.error('Failed to load dashboard:', error);
        kpisDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
}

function renderKPIs(monthlyData) {
    const kpisDiv = document.getElementById('kpis');
    if (!monthlyData || monthlyData.length === 0) {
        kpisDiv.innerHTML = '<p>No data available for this period.</p>';
        return;
    }

    const totalCosts = monthlyData.reduce((sum, d) => sum + d.financials.purchase_costs, 0);
    const totalRevenue = monthlyData.reduce((sum, d) => sum + d.financials.feed_in_revenue, 0);
    const totalNetResult = totalRevenue - totalCosts;
    const avgSelfSufficiency = monthlyData.reduce((sum, d) => sum + d.energy_flow.self_sufficiency_percent, 0) / monthlyData.length;

    kpisDiv.innerHTML = `
        <div><strong>Totale Kosten:</strong> € ${totalCosts.toFixed(2)}</div>
        <div><strong>Totale Opbrengsten:</strong> € ${totalRevenue.toFixed(2)}</div>
        <div><strong>Netto Resultaat:</strong> € ${totalNetResult.toFixed(2)}</div>
        <div><strong>Gem. Zelfvoorzienendheid:</strong> ${avgSelfSufficiency.toFixed(1)} %</div>
    `;
}

function renderRoiTracker(roiData) {
    const roiDiv = document.getElementById('roi-tracker');
    const percentage = (roiData.total_earned / roiData.total_investment) * 100;

    roiDiv.innerHTML = `
        <p>
            <strong>€ ${roiData.total_earned.toFixed(2)}</strong> van
            <strong>€ ${roiData.total_investment.toFixed(2)}</strong> terugverdiend.
            (Nog te gaan: € ${roiData.remaining_balance.toFixed(2)})
        </p>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: ${percentage.toFixed(2)}%;">
                ${percentage.toFixed(1)}%
            </div>
        </div>
        <small>Methode: ${roiData.calculation_method}</small>
    `;
}

function renderEnergyBalanceChart(monthlyData) {
    const ctx = document.getElementById('energyBalanceChart').getContext('2d');
    const labels = monthlyData.map(d => d.period);

    const datasets = [
        {
            label: 'Import (kWh)',
            data: monthlyData.map(d => d.energy_flow.total_consumption_kwh - d.energy_flow.self_consumption_kwh),
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
        },
        {
            label: 'Export (kWh)',
            data: monthlyData.map(d => d.energy_flow.self_consumption_kwh > 0 ? (d.energy_flow.self_consumption_kwh / d.energy_flow.self_consumption_ratio_percent * 100) - d.energy_flow.self_consumption_kwh : 0 ),
            backgroundColor: 'rgba(255, 206, 86, 0.5)',
        },
        {
            label: 'Opgewekt (kWh)',
            data: monthlyData.map(d => d.energy_flow.self_consumption_kwh > 0 ? (d.energy_flow.self_consumption_kwh / d.energy_flow.self_consumption_ratio_percent * 100) : 0),
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
        },
        {
            label: 'Eigen Verbruik (kWh)',
            data: monthlyData.map(d => d.energy_flow.self_consumption_kwh),
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
        }
    ];

    if (energyBalanceChartInstance) {
        energyBalanceChartInstance.destroy();
    }

    energyBalanceChartInstance = new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            scales: {
                x: { stacked: true },
                y: { stacked: true, beginAtZero: true }
            }
        }
    });
}

function renderConsumptionSplitChart(monthlyData) {
    const ctx = document.getElementById('consumptionSplitChart').getContext('2d');
    const totalHome = monthlyData.reduce((sum, d) => sum + d.energy_flow.home_consumption_kwh, 0);
    const totalEV = monthlyData.reduce((sum, d) => sum + (d.energy_flow.total_consumption_kwh - d.energy_flow.home_consumption_kwh), 0);

    if (consumptionSplitChartInstance) {
        consumptionSplitChartInstance.destroy();
    }

    consumptionSplitChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Huis Verbruik (kWh)', 'Auto/EV Verbruik (kWh)'],
            datasets: [{
                data: [totalHome, totalEV],
                backgroundColor: ['rgba(153, 102, 255, 0.5)', 'rgba(255, 159, 64, 0.5)']
            }]
        }
    });
}

// --- METRIC FORM SUBMISSION ---
async function handleMetricFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const statusDiv = document.getElementById('form-status');

    const data = {};
    formData.forEach((value, key) => { data[key] = value; });

    if (data.period) {
        data.period = `${data.period}-01`;
    }

    statusDiv.textContent = 'Submitting...';
    statusDiv.style.color = 'blue';

    try {
        const response = await fetch('/api/v1/metrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            const result = await response.json();
            statusDiv.textContent = `Success! Metric for period ${result.period} created with ID ${result.id}.`;
            statusDiv.style.color = 'green';
            form.reset();
        } else {
            const error = await response.json();
            statusDiv.textContent = `Error: ${error.detail || 'Failed to submit data.'}`;
            statusDiv.style.color = 'red';
        }
    } catch (error) {
        console.error('Submission error:', error);
        statusDiv.textContent = 'A network error occurred. Please try again.';
        statusDiv.style.color = 'red';
    }
}
