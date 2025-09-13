import pytest
from decimal import Decimal
from app.models.models import MonthlyJournal
from app.services.energy_calculations import calculate_energy_flow

@pytest.fixture
def sample_journal():
    """Provides a sample MonthlyJournal object for testing."""
    return MonthlyJournal(
        solar_production_kwh=1000.0,
        grid_feed_in_low_kwh=300.0,
        grid_feed_in_high_kwh=100.0,
        grid_consumption_low_kwh=100.0,
        grid_consumption_high_kwh=50.0,
        battery_charge_kwh=200.0,
        battery_discharge_kwh=180.0
    )

def test_calculate_energy_flow(sample_journal):
    """
    Tests the calculate_energy_flow function with a sample journal.
    """
    # Act
    result = calculate_energy_flow(sample_journal)

    # Assert
    # Total grid feed in = 300 + 100 = 400
    # Self-consumption = Production - Total Grid Feed In = 1000 - 400 = 600
    # Total consumption = Grid Consumption + Self-consumption = (100 + 50) + 600 = 750
    # Home consumption = Total Consumption - Battery Charge = 750 - 200 = 550
    # Self-sufficiency = Self-consumption / Total Consumption = 600 / 750 = 0.8

    assert result["total_grid_feed_in_kwh"] == Decimal('400.0')
    assert result["self_consumption_kwh"] == Decimal('600.0')
    assert result["total_household_consumption_kwh"] == Decimal('750.0')
    assert result["home_consumption_kwh"] == Decimal('550.0')
    assert result["self_sufficiency_ratio"] == Decimal('0.8')

def test_calculate_energy_flow_no_consumption(sample_journal):
    """
    Tests the case where there is no grid consumption.
    """
    sample_journal.grid_consumption_low_kwh = 0.0
    sample_journal.grid_consumption_high_kwh = 0.0

    # Act
    result = calculate_energy_flow(sample_journal)

    # Assert
    # Total grid feed in = 400
    # Self-consumption = 1000 - 400 = 600
    # Total consumption = 0 + 600 = 600
    # Home consumption = 600 - 200 = 400
    # Self-sufficiency = 600 / 600 = 1.0
    assert result["total_household_consumption_kwh"] == Decimal('600.0')
    assert result["home_consumption_kwh"] == Decimal('400.0')
    assert result["self_sufficiency_ratio"] == Decimal('1.0')

def test_calculate_energy_flow_no_production():
    """
    Tests the case where there is no production.
    """
    journal = MonthlyJournal(
        solar_production_kwh=0.0,
        grid_feed_in_low_kwh=0.0,
        grid_feed_in_high_kwh=0.0,
        grid_consumption_low_kwh=100.0,
        grid_consumption_high_kwh=50.0,
        battery_charge_kwh=0.0,
        battery_discharge_kwh=0.0
    )

    # Act
    result = calculate_energy_flow(journal)

    # Assert
    assert result["self_consumption_kwh"] == Decimal('0.0')
    assert result["total_household_consumption_kwh"] == Decimal('150.0')
    assert result["home_consumption_kwh"] == Decimal('150.0')
    assert result["self_sufficiency_ratio"] == Decimal('0.0')
