import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from decimal import Decimal

from app.services.roi_calculations import calculate_roi_status
from app.models.models import Investment, MonthlyMetric, Tariff
from app.schemas.roi import ROIStatus, ROIMethodResult

class TestROICalculations(unittest.TestCase):

    @patch('app.services.roi_calculations.crud_investments')
    @patch('app.services.roi_calculations.crud_metrics')
    @patch('app.services.roi_calculations.crud_tariffs')
    @patch('app.services.roi_calculations.energy_calculations')
    @patch('app.services.roi_calculations.financial_calculations')
    def test_calculate_roi_status(self, mock_financial_calculations, mock_energy_calculations, mock_crud_tariffs, mock_crud_metrics, mock_crud_investments):
        # Mocking the database session
        mock_db = MagicMock()

        # Mocking the investment
        mock_investment = Investment(
            id=1,
            installation_date=date(2023, 1, 1),
            total_cost_eur=Decimal('10000.00'),
        )
        mock_crud_investments.get.return_value = mock_investment

        # Mocking metrics
        mock_metrics = [
            MonthlyMetric(
                period_start=date(2023, 1, 1),
                production_total_kwh=100,
                export_total_kwh=50,
                import_low_kwh=10,
                import_high_kwh=10,
                consumption_ev_kwh=0,
                battery_charge_kwh=0,
                battery_discharge_kwh=0,
            ),
            MonthlyMetric(
                period_start=date(2023, 2, 1),
                production_total_kwh=120,
                export_total_kwh=60,
                import_low_kwh=12.5,
                import_high_kwh=12.5,
                consumption_ev_kwh=0,
                battery_charge_kwh=0,
                battery_discharge_kwh=0,
            ),
        ]
        mock_crud_metrics.get_metrics_by_investment.return_value = mock_metrics

        # Mocking tariff
        mock_tariff = Tariff(
            purchase_high_eur_kwh=Decimal('0.25'),
            fixed_roi_rate_eur_kwh=Decimal('0.10'),
        )
        mock_crud_tariffs.get_active_tariff.return_value = mock_tariff

        # Mocking energy and financial calculations
        # In the first month, self_consumption is 100 - 50 = 50
        # In the second month, self_consumption is 120 - 60 = 60
        mock_energy_calculations.calculate_energy_flow.side_effect = [
            {'self_consumption_kwh': 50},
            {'self_consumption_kwh': 60}
        ]
        mock_financial_calculations.calculate_financials.side_effect = [
            {'export_revenue_ex_vat': Decimal('12.5')},
            {'export_revenue_ex_vat': Decimal('15.0')}
        ]

        # Call the function
        roi_status = calculate_roi_status(mock_db, 1)

        # Assertions
        self.assertIsNotNone(roi_status)
        # Method 1
        # Month 1: (50 * 0.25) + 12.5 = 12.5 + 12.5 = 25
        # Month 2: (60 * 0.25) + 15.0 = 15.0 + 15.0 = 30
        # Total: 25 + 30 = 55
        self.assertAlmostEqual(roi_status.method_1.cumulative_savings, 55, places=2)
        self.assertAlmostEqual(roi_status.method_1.remaining_balance, 10000 - 55, places=2)
        self.assertAlmostEqual(roi_status.method_1.progress_percentage, (55/10000)*100, places=2)

        # Method 2
        # Month 1: 100 * 0.10 = 10
        # Month 2: 120 * 0.10 = 12
        # Total: 10 + 12 = 22
        self.assertAlmostEqual(roi_status.method_2.cumulative_savings, 22, places=2)
        self.assertAlmostEqual(roi_status.method_2.remaining_balance, 10000 - 22, places=2)
        self.assertAlmostEqual(roi_status.method_2.progress_percentage, (22/10000)*100, places=2)

if __name__ == '__main__':
    unittest.main()
