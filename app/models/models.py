from sqlalchemy import Column, Integer, String, Float, Date, Numeric
from app.db.session import Base


class Investment(Base):
    """
    SQLAlchemy model for an investment (e.g., solar panel installation).

    Attributes:
        id: Primary key.
        description: A text description of the investment.
        installation_date: The date the investment was installed.
        total_cost_eur: The total cost of the investment in Euros.
        total_power_wp: The total peak power of the installation in Watt-peak.
        estimated_annual_production_kwh: The estimated annual energy
                                           production in kWh.
    """
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    installation_date = Column(Date, nullable=False)
    total_cost_eur = Column(Numeric(10, 2), nullable=False)
    total_power_wp = Column(Integer, nullable=False)
    estimated_annual_production_kwh = Column(Integer)


class Tariff(Base):
    """
    SQLAlchemy model for an energy tariff.

    Attributes:
        id: Primary key.
        start_date: The date the tariff becomes active.
        end_date: The date the tariff expires. Can be null for ongoing tariffs.
        purchase_low_eur_kwh: The cost per kWh for low-rate electricity purchase.
        purchase_high_eur_kwh: The cost per kWh for high-rate electricity purchase.
        sale_eur_kwh: The revenue per kWh for selling electricity.
        vat_percentage: The VAT percentage applicable to energy costs.
        fixed_roi_rate_eur_kwh: An optional fixed rate for ROI calculations,
                                in Euros per kWh.
    """
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    purchase_low_eur_kwh = Column(Numeric(10, 5), nullable=False)
    purchase_high_eur_kwh = Column(Numeric(10, 5), nullable=False)
    sale_eur_kwh = Column(Numeric(10, 5), nullable=False)
    vat_percentage = Column(Numeric(5, 2), default=0.21)
    fixed_roi_rate_eur_kwh = Column(Numeric(10, 5), nullable=True)


class MonthlyMetric(Base):
    """
    SQLAlchemy model for monthly energy metrics.

    Attributes:
        id: Primary key.
        period_start: The start date of the month for which metrics are recorded.
        account_name: The name of the account associated with the metrics.
        production_total_kwh: Total electricity produced in kWh.
        import_low_kwh: Total low-rate electricity imported in kWh.
        import_high_kwh: Total high-rate electricity imported in kWh.
        export_total_kwh: Total electricity exported in kWh.
        consumption_ev_kwh: Electricity consumed by an electric vehicle in kWh.
        battery_charge_kwh: Electricity used to charge a battery in kWh.
        battery_discharge_kwh: Electricity discharged from a battery in kWh.
        monthly_prepayment_eur: The monthly prepayment amount in Euros.
    """
    __tablename__ = "monthly_metrics"

    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(Date, nullable=False, unique=True)
    account_name = Column(String, nullable=False)
    production_total_kwh = Column(Float)
    import_low_kwh = Column(Float)
    import_high_kwh = Column(Float)
    export_total_kwh = Column(Float)
    consumption_ev_kwh = Column(Float)
    battery_charge_kwh = Column(Float, default=0.0)
    battery_discharge_kwh = Column(Float, default=0.0)
    monthly_prepayment_eur = Column(Numeric(10, 2))
