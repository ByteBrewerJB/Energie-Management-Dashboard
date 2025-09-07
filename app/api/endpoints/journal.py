from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api import deps
from app.schemas import journal as journal_schema
from app.crud import crud_journal

router = APIRouter()


from decimal import Decimal
from app.services import financial_calculations, energy_calculations

@router.get("/{year}", response_model=List[journal_schema.FrontendChartData])
def read_journals_for_year(
    year: int,

    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """

    Retrieve all monthly journal entries for a specific year, run calculations,
    and return the data in the format expected by the frontend.
    """
    db_journals = crud_journal.get_or_create_journals_for_year(db, year=year)

    response_data = []
    for journal in db_journals:
        # 1. Perform financial calculations
        statement = financial_calculations.calculate_monthly_statement(journal)

        # 2. Perform energy flow calculations
        energy_flow_dict = energy_calculations.calculate_energy_flow(journal)

        # 3. Assemble the data into the structure the frontend expects

        # The frontend expects `import_total_kwh` which is not in the energy_flow dict.
        # We calculate it here from the raw journal data.
        import_total_kwh = (journal.grid_consumption_low_kwh or 0) + \
                            (journal.grid_consumption_high_kwh or 0)

        # The frontend also expects `export_total_kwh` on the metric object itself,
        # but the calculation service puts it in `total_grid_feed_in_kwh`. Let's align that.
        # We can add it to the journal object before creating the Pydantic model.
        journal.export_total_kwh = energy_flow_dict.get("total_grid_feed_in_kwh", 0)


        energy_flow = journal_schema.EnergyFlow(
            self_consumption_kwh=energy_flow_dict.get("self_consumption_kwh", 0),
            total_household_consumption_kwh=energy_flow_dict.get("total_household_consumption_kwh", 0),
            home_consumption_kwh=energy_flow_dict.get("home_consumption_kwh", 0),
            self_sufficiency_ratio=energy_flow_dict.get("self_sufficiency_ratio", 0),
            total_grid_feed_in_kwh=energy_flow_dict.get("total_grid_feed_in_kwh", 0),
            import_total_kwh=import_total_kwh
        )

        financials = journal_schema.Financials(
            net_costs=statement.net_energy_cost_eur
        )

        # The frontend expects the raw journal data under the 'metric' key
        metric = journal_schema.MonthlyJournal.model_validate(journal)

        chart_data = journal_schema.FrontendChartData(
            metric=metric,
            financials=financials,
            energy_flow=energy_flow
        )
        response_data.append(chart_data)

    return response_data


@router.put("/{year}/{month}", response_model=journal_schema.MonthlyJournal)
def update_monthly_journal(
    year: int,
    month: int,
    *,
    db: Session = Depends(get_db),
    journal_in: journal_schema.MonthlyJournalUpdate,
    current_user: str = Depends(deps.get_current_user)
):
    """
    Update a monthly journal entry.
    """
    journal = crud_journal.update_journal(db=db, year=year, month=month, obj_in=journal_in)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found for this period.")
    return journal
