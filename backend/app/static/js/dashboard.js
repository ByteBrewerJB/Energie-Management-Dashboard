(function () {
    if (typeof Chart === 'undefined' || !window.dashboardData) {
        return;
    }

    const labels = dashboardData.kpis.map((item) => item.month_label);

    const energyCtx = document.getElementById('energyBalanceChart');
    if (energyCtx) {
        const netImport = dashboardData.energy_balance.map((item) => item.net_import_kwh);
        const selfConsumption = dashboardData.energy_balance.map((item) => item.self_consumption_kwh);
        const netExport = dashboardData.energy_balance.map((item) => item.net_export_kwh);

        new Chart(energyCtx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: 'Netto import', data: netImport, backgroundColor: '#ef4444' },
                    { label: 'Zelfverbruik', data: selfConsumption, backgroundColor: '#3b82f6' },
                    { label: 'Netto export', data: netExport, backgroundColor: '#22c55e' },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    x: { stacked: true },
                    y: { stacked: true, beginAtZero: true },
                },
            },
        });
    }

    const consumptionCtx = document.getElementById('consumptionSplitChart');
    if (consumptionCtx) {
        const totals = dashboardData.consumption_split.reduce(
            (acc, month) => {
                acc.household += month.household_kwh;
                acc.ev += month.ev_kwh;
                return acc;
            },
            { household: 0, ev: 0 }
        );
        new Chart(consumptionCtx, {
            type: 'doughnut',
            data: {
                labels: ["Huishouden", "Elektrische auto's"],
                datasets: [
                    {
                        data: [totals.household, totals.ev],
                        backgroundColor: ['#0ea5e9', '#a855f7'],
                    },
                ],
            },
            options: {
                responsive: true,
            },
        });
    }

    const productionCtx = document.getElementById('productionChart');
    if (productionCtx) {
        const actual = dashboardData.production_vs_expectation.map((item) => item.actual_production_kwh);
        const expected = dashboardData.production_vs_expectation.map((item) => item.expected_production_kwh);
        new Chart(productionCtx, {
            data: {
                labels,
                datasets: [
                    { type: 'line', label: 'Productie', data: actual, borderColor: '#3b82f6', fill: false, tension: 0.3 },
                    { type: 'line', label: 'Verwachting', data: expected, borderColor: '#94a3b8', borderDash: [6, 4], fill: false, tension: 0.1 },
                ],
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: { beginAtZero: true },
                },
            },
        });
    }

    const financialCtx = document.getElementById('financialChart');
    if (financialCtx) {
        const consumptionCosts = dashboardData.financials.map((item) => item.consumption_costs_eur);
        const feedInRevenue = dashboardData.financials.map((item) => item.feed_in_revenue_eur);
        const carReimbursement = dashboardData.financials.map((item) => item.car_reimbursement_eur);
        const finalSettlement = dashboardData.financials.map((item) => item.final_settlement_eur);

        new Chart(financialCtx, {
            data: {
                labels,
                datasets: [
                    { type: 'bar', label: 'Kosten verbruik', data: consumptionCosts, backgroundColor: '#3b82f6' },
                    { type: 'bar', label: 'Opbrengst teruglevering', data: feedInRevenue, backgroundColor: '#22c55e' },
                    { type: 'bar', label: 'Vergoeding auto', data: carReimbursement, backgroundColor: '#f59e0b' },
                    { type: 'line', label: 'Eindafrekening', data: finalSettlement, borderColor: '#ef4444', tension: 0.2, yAxisID: 'y1' },
                ],
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: { beginAtZero: true },
                    y1: {
                        position: 'right',
                        beginAtZero: true,
                        grid: { drawOnChartArea: false },
                    },
                },
            },
        });
    }
})();
