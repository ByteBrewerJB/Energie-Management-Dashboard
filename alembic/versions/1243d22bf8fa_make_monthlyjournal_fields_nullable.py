"""Make MonthlyJournal fields nullable

Revision ID: 1243d22bf8fa
Revises: 5e2d3bd5e9c1
Create Date: 2025-09-07 08:02:12.252272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1243d22bf8fa'
down_revision: Union[str, Sequence[str], None] = '5e2d3bd5e9c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('monthly_metrics', 'grid_consumption_low_kwh',
               existing_type=sa.FLOAT(),
               nullable=True)
    op.alter_column('monthly_metrics', 'grid_consumption_high_kwh',
               existing_type=sa.FLOAT(),
               nullable=True)
    op.alter_column('monthly_metrics', 'grid_feed_in_low_kwh',
               existing_type=sa.FLOAT(),
               nullable=True)
    op.alter_column('monthly_metrics', 'grid_feed_in_high_kwh',
               existing_type=sa.FLOAT(),
               nullable=True)
    op.alter_column('tariffs', 'consumption_price_low_eur_kwh',
               existing_type=sa.NUMERIC(precision=10, scale=5),
               nullable=True)
    op.alter_column('tariffs', 'consumption_price_high_eur_kwh',
               existing_type=sa.NUMERIC(precision=10, scale=5),
               nullable=True)
    op.alter_column('tariffs', 'feed_in_tariff_low_eur_kwh',
               existing_type=sa.NUMERIC(precision=10, scale=5),
               nullable=True)
    op.alter_column('tariffs', 'feed_in_tariff_high_eur_kwh',
               existing_type=sa.NUMERIC(precision=10, scale=5),
               nullable=True)
    op.alter_column('monthly_metrics', 'battery_charge_kwh',
               existing_type=sa.FLOAT(),
               nullable=True)
    op.alter_column('monthly_metrics', 'battery_discharge_kwh',
               existing_type=sa.FLOAT(),
               nullable=True)
    op.alter_column('monthly_metrics', 'monthly_prepayment_eur',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('monthly_metrics', 'monthly_prepayment_eur',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
    op.alter_column('monthly_metrics', 'battery_discharge_kwh',
               existing_type=sa.FLOAT(),
               nullable=False)
    op.alter_column('monthly_metrics', 'battery_charge_kwh',
               existing_type=sa.FLOAT(),
               nullable=False)
    op.alter_column('tariffs', 'feed_in_tariff_high_eur_kwh',
               existing_type=sa.NUMERIC(precision=10, scale=5),
               nullable=False)
    op.alter_column('tariffs', 'feed_in_tariff_low_eur_kwh',
               existing_type=sa.NUMERIC(precision=10, scale=5),
               nullable=False)
    op.alter_column('tariffs', 'consumption_price_high_eur_kwh',
               existing_type=sa.NUMERIC(precision=10, scale=5),
               nullable=False)
    op.alter_column('tariffs', 'consumption_price_low_eur_kwh',
               existing_type=sa.NUMERIC(precision=10, scale=5),
               nullable=False)
    op.alter_column('monthly_metrics', 'grid_feed_in_high_kwh',
               existing_type=sa.FLOAT(),
               nullable=False)
    op.alter_column('monthly_metrics', 'grid_feed_in_low_kwh',
               existing_type=sa.FLOAT(),
               nullable=False)
    op.alter_column('monthly_metrics', 'grid_consumption_high_kwh',
               existing_type=sa.FLOAT(),
               nullable=False)
    op.alter_column('monthly_metrics', 'grid_consumption_low_kwh',
               existing_type=sa.FLOAT(),
               nullable=False)
