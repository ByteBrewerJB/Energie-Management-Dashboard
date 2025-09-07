import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from decimal import Decimal

from app.services.roi_calculations import calculate_solar_panel_roi, calculate_battery_roi
from app.models.models import SolarPanel, Battery, MonthlyJournal
from app.schemas.roi import ROIStatus, ROIMethodResult

class TestNewROICalculations(unittest.TestCase):

    @patch('app.services.roi_calculations.crud_solar_panel')
    @patch('app.services.roi_calculations.energy_calculations')
    def test_calculate_solar_panel_roi(self, mock_energy, mock_crud_solar_panel):
        mock_db = MagicMock()

        # Mock Solar Panel
        mock_solar_panel = SolarPanel(
            id=1,
            purchase_date=date(2023, 1, 1),
            purchase_cost_eur=Decimal('10000.00'),
        )
        mock_crud_solar_panel.get.return_value = mock_solar_panel

        # Mock Journals
        mock_journal = MonthlyJournal(
            year=2023,
            month=1,
            grid_consumption_low_kwh=10.0,
            grid_consumption_high_kwh=10.0,
            grid_feed_in_low_kwh=20.0,
            grid_feed_in_high_kwh=30.0,
            consumption_price_low_eur_kwh=Decimal('0.20'),
            consumption_price_high_eur_kwh=Decimal('0.30'),
            feed_in_tariff_low_eur_kwh=Decimal('0.05'),
            feed_in_tariff_high_eur_kwh=Decimal('0.08'),
        )
        # Mock the query chain
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_journal]

        # Mock service calculations
        mock_energy.calculate_energy_flow.return_value = {'self_consumption_kwh': Decimal('50.0')}

        # Call function
        roi_status = calculate_solar_panel_roi(mock_db, 1)

        # Assertions
        # Feed-in revenue = (20 * 0.05) + (30 * 0.08) = 1.0 + 2.4 = 3.4
        # Avg consumption price = ((10 * 0.20) + (10 * 0.30)) / 20 = (2 + 3) / 20 = 0.25
        # Avoided costs = 50 * 0.25 = 12.5
        # Total savings = 3.4 + 12.5 = 15.9
        self.assertAlmostEqual(roi_status.method_1.cumulative_savings, 15.9, places=2)
        self.assertAlmostEqual(roi_status.method_1.remaining_balance, 10000 - 15.9, places=2)

    @patch('app.services.roi_calculations.crud_battery')
    def test_calculate_battery_roi(self, mock_crud_battery):
        mock_db = MagicMock()

        # Mock Battery
        mock_battery = Battery(
            id=1,
            purchase_date=date(2023, 1, 1),
            purchase_cost_eur=Decimal('5000.00'),
        )
        mock_crud_battery.get.return_value = mock_battery

        # Mock Journals
        mock_journal = MonthlyJournal(
            year=2023,
            month=1,
            battery_charge_kwh=50.0,
            battery_discharge_kwh=45.0,
            consumption_price_low_eur_kwh=Decimal('0.20'),
            consumption_price_high_eur_kwh=Decimal('0.30'),
        )
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_journal]

        # Call function
        roi_status = calculate_battery_roi(mock_db, 1)

        # Assertions
        # Avoided cost = 45 * 0.30 = 13.5
        # Charge cost = 50 * 0.20 = 10.0
        # Monthly savings = 13.5 - 10.0 = 3.5
        self.assertAlmostEqual(roi_status.method_1.cumulative_savings, 3.5, places=2)
        self.assertAlmostEqual(roi_status.method_1.remaining_balance, 5000 - 3.5, places=2)

if __name__ == '__main__':
    unittest.main()
