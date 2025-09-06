import unittest
from unittest.mock import MagicMock
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud import crud_investments
from app.models.models import Investment
from app.schemas.investment import InvestmentCreate, InvestmentUpdate

class TestCrudInvestments(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock(spec=Session)

    def test_create_investment(self):
        investment_in = InvestmentCreate(
            description="Test Investment",
            installation_date=date(2023, 1, 1),
            total_cost_eur=Decimal('10000.00'),
            total_power_wp=5000,
            estimated_annual_production_kwh=5000,
        )
        crud_investments.create(self.db, obj_in=investment_in)
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()

    def test_get_investment(self):
        crud_investments.get(self.db, investment_id=1)
        self.db.query.assert_called_once_with(Investment)

    def test_get_multi_investments(self):
        crud_investments.get_multi(self.db)
        self.db.query.assert_called_once_with(Investment)

    def test_update_investment(self):
        db_obj = Investment()
        obj_in = InvestmentUpdate(description="Updated Description")
        crud_investments.update(self.db, db_obj=db_obj, obj_in=obj_in)
        self.assertEqual(db_obj.description, "Updated Description")
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()

    def test_remove_investment(self):
        db_obj = Investment()
        self.db.query.return_value.filter.return_value.first.return_value = db_obj
        crud_investments.remove(self.db, investment_id=1)
        self.db.delete.assert_called_once_with(db_obj)
        self.db.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
