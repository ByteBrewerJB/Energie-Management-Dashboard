import pytest
from app.models.models import MonthlyMetric
from app.services.energy_calculations import calculate_energy_flow

def test_calculate_energy_flow_with_battery():
    # Arrange
    metric = MonthlyMetric(
        production_total_kwh=1000,
        export_total_kwh=400,
        import_low_kwh=100,
        import_high_kwh=50,
        consumption_ev_kwh=150,
        battery_charge_kwh=200,
        battery_discharge_kwh=180  # Discharge doesn't affect this calculation
    )

    # Act
    result = calculate_energy_flow(metric)

    # Assert
    # Self-consumption = Production - Export = 1000 - 400 = 600
    # Total consumption = Import_Low + Import_High + Self-consumption
    #                   = 100 + 50 + 600 = 750
    # Expected home consumption (buggy) = Total Consumption - EV Consumption
    #                                   = 750 - 150 = 600
    # Expected home consumption (fixed) = Total Consumption - EV Consumption - Battery Charge
    #                                   = 750 - 150 - 200 = 400

    # This assertion should fail before the fix
    assert result['home_consumption_kwh'] == 400
