// JouleJournal Dashboard - Main Application Logic

const API_URL = '/api';

/**
 * A wrapper around the fetch API that adds the Authorization header
 * and handles 401 Unauthorized responses by redirecting to the login page.
 * @param {string} url The URL to fetch.
 * @param {object} options The options for the fetch request.
 * @returns {Promise<any>} A promise that resolves to the JSON response.
 */
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('access_token');

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        // Token is invalid or expired
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        // Throw an error to stop further processing
        throw new Error('Session expired. Please log in again.');
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
        throw new Error(errorData.detail);
    }

    return response.json();
}


// Store chart instances to destroy them before re-rendering
let energyBalanceChartInstance = null;
let consumptionSplitChartInstance = null;
let productionForecastChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return; // Stop executing script if not authenticated
    }

    const themeSwitch = document.getElementById('checkbox');
    if (themeSwitch) {
        // Set the default theme to light. Check localStorage for 'dark-mode' override.
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme === 'dark-mode') {
            document.body.classList.add('dark-mode');
            themeSwitch.checked = true;
        }

        // Listen for theme changes
        themeSwitch.addEventListener('change', function(event) {
            if (event.target.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.removeItem('theme'); // Light theme is the default
            }
        });
    }

    console.log('JouleJournal Dashboard Initialized.');
    loadAllData();
});

/**
 * Fetches all necessary data from the backend API concurrently.
 */
async function loadAllData() {
    const kpiContainer = document.getElementById('kpi-card');
    const kpisDiv = document.getElementById('kpis');
    kpisDiv.innerHTML = '<p>Loading dashboard data...</p>';

    const year = new Date().getFullYear();

    try {
        const timeseriesPromise = fetchWithAuth(`${API_URL}/metrics/${year}`);

        const roiPromise = fetchWithAuth(`${API_URL}/investments`)
            .then(investments => {
                const solarPanel = investments.find(inv => inv.type === 'solar_panel');
                if (solarPanel) {
                    return fetchWithAuth(`${API_URL}/roi/solar_panels/${solarPanel.id}`);
                }
                return null; // No solar panel found
            });

        // As discovered during exploration, there is no forecast endpoint.
        // We will provide a dummy structure to prevent the chart rendering from failing.
        const forecastPromise = Promise.resolve({
            forecast: {
                forecast: [] // Empty array to signify no data
            }
        });

        const [timeseriesData, roiData, forecastData] = await Promise.all([
            timeseriesPromise,
            roiPromise,
            forecastPromise
        ]);

        if (!timeseriesData || timeseriesData.length === 0) {
            kpisDiv.innerHTML = '<p>No dashboard data available for the current year. Please add data via the admin panel.</p>';
            return;
        }

        // Render all the components with the fetched data
        renderKPIs(timeseriesData, year);
        renderRoiTracker(roiData);
        renderEnergyBalanceChart(timeseriesData);
        renderConsumptionSplitChart(timeseriesData);
        renderProductionForecastChart(timeseriesData, forecastData);

    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        // The fetchWithAuth function handles redirects for 401,
        // so we only need to show a generic error for other issues.
        const errorHtml = `
            <div class="error-message">
                <strong>Error loading dashboard</strong>
                <p>${error.message}</p>
            </div>
        `;
        if (kpiContainer) {
            kpiContainer.innerHTML = errorHtml;
        } else {
            kpisDiv.innerHTML = errorHtml;
        }
    }
}

/**
 * Renders Key Performance Indicators for the specified year.
 */
function renderKPIs(timeseriesData, year) {
    const kpisDiv = document.getElementById('kpis');
    if (!timeseriesData || timeseriesData.length === 0) {
        kpisDiv.innerHTML = '<p>No data available for the current year.</p>';
        return;
    }

    const totalNetCosts = timeseriesData.reduce((sum, data) => sum + data.financials.net_costs, 0);
    const totalSelfSufficiency = timeseriesData.reduce((sum, data) => sum + data.energy_flow.self_sufficiency_ratio, 0);
    const averageSelfSufficiency = totalSelfSufficiency / timeseriesData.length * 100; // as percentage

    kpisDiv.innerHTML = `
        <div class="kpi-item">
            <h3>Totaal Netto Kosten (${year})</h3>
            <p>€ ${totalNetCosts.toFixed(2)}</p>
        </div>
        <div class="kpi-item">
            <h3>Gem. Zelfvoorzienendheid</h3>
            <p>${averageSelfSufficiency.toFixed(1)} %</p>
        </div>
    `;
}

/**
 * Renders the ROI tracker progress bar.
 */
function renderRoiTracker(roiData) {
    const roiDiv = document.getElementById('roi-tracker');
    if (!roiData) {
        roiDiv.innerHTML = '<p>ROI data not available.</p>';
        return;
    }

    const { progress_percentage, cumulative_savings, remaining_balance } = roiData;

    roiDiv.innerHTML = `
        <div class="roi-summary">
             <p><strong>Voortgang:</strong> € ${cumulative_savings.toFixed(2)} / € ${(cumulative_savings + remaining_balance).toFixed(2)}</p>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: ${progress_percentage.toFixed(2)}%;">
                ${progress_percentage.toFixed(1)}%
            </div>
        </div>
         <div class="roi-details">
            <span>Besparing: € ${cumulative_savings.toFixed(2)}</span>
            <span>Resterend: € ${remaining_balance.toFixed(2)}</span>
        </div>
    `;
}


/**
 * Renders the stacked bar chart for energy balance.
 */
function renderEnergyBalanceChart(timeseriesData) {
    const ctx = document.getElementById('energyBalanceChart').getContext('2d');
    const labels = timeseriesData.map(d => new Date(d.metric.period_start).toLocaleString('default', { month: 'short' }));

    const datasets = [
        {
            label: 'Import (kWh)',
            data: timeseriesData.map(d => d.energy_flow.import_total_kwh),
            backgroundColor: '#FF6384',
        },
        {
            label: 'Eigen Verbruik (kWh)',
            data: timeseriesData.map(d => d.energy_flow.self_consumption_kwh),
            backgroundColor: '#36A2EB',
        },
        {
            label: 'Export (kWh)',
            data: timeseriesData.map(d => d.metric.export_total_kwh),
            backgroundColor: '#FFCE56',
        }
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
                title: { display: true, text: 'Maandelijkse Energiebalans (Import, Export, Eigen Verbruik)' },
                tooltip: { mode: 'index', intersect: false },
            },
            scales: {
                x: { stacked: true },
                y: { stacked: true, beginAtZero: true, title: { display: true, text: 'kWh' } }
            }
        }
    });
}

/**
 * Renders the pie chart for consumption breakdown.
 */
function renderConsumptionSplitChart(timeseriesData) {
    const ctx = document.getElementById('consumptionSplitChart').getContext('2d');

    const totalHomeConsumption = timeseriesData.reduce((sum, d) => sum + d.energy_flow.home_consumption_kwh, 0);
    const totalEvConsumption = timeseriesData.reduce((sum, d) => sum + d.metric.consumption_ev_kwh, 0);

    if (consumptionSplitChartInstance) {
        consumptionSplitChartInstance.destroy();
    }

    consumptionSplitChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Huis Verbruik', 'Auto (EV) Verbruik'],
            datasets: [{
                data: [totalHomeConsumption, totalEvConsumption],
                backgroundColor: ['#4BC0C0', '#9966FF'],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Uitsplitsing Totaal Verbruik (Huidig Jaar)' },
            }
        }
    });
}

/**
 * Renders the line chart comparing actual production with the forecast.
 */
function renderProductionForecastChart(timeseriesData, forecastData) {
    const ctx = document.getElementById('productionForecastChart').getContext('2d');

    const labels = forecastData.forecast.map(f => f.month);
    const forecastValues = forecastData.forecast.map(f => f.kwh);

    // Create a map for quick lookup of actual production by month name
    const actualsMap = new Map();
    timeseriesData.forEach(d => {
        const monthName = new Date(d.metric.period_start).toLocaleString('default', { month: 'short' });
        actualsMap.set(monthName, d.metric.production_total_kwh);
    });

    // Align actual data with forecast labels
    const actualValues = labels.map(label => actualsMap.get(label) || 0);

    if (productionForecastChartInstance) {
        productionForecastChartInstance.destroy();
    }

    productionForecastChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Werkelijke Productie (kWh)',
                    data: actualValues,
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Verwachte Productie (kWh)',
                    data: forecastValues,
                    borderColor: '#FF6384',
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderDash: [5, 5], // Dashed line for forecast
                    fill: false,
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Werkelijke Productie vs. Forecast' },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'kWh' }
                }
            }
        }
    });
}
