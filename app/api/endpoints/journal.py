from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api import deps
from app.schemas import journal as journal_schema
from app.crud import crud_journal
from app.models import models

router = APIRouter()

from decimal import Decimal
from app.services import financial_calculations, energy_calculations

from fastapi import status

def _get_processed_journal_data(journal: models.MonthlyJournal) -> journal_schema.FrontendChartData:
    """
    Takes a raw journal entry from the DB and returns the fully processed
    data structure expected by the frontend.
    """
    # 1. Perform financial calculations
    statement = financial_calculations.calculate_monthly_statement(journal)

    # 2. Perform energy flow calculations
    energy_flow_dict = energy_calculations.calculate_energy_flow(journal)

    # 3. Assemble the data into the structure the frontend expects
    import_total_kwh = (journal.grid_consumption_low_kwh or 0) + \
                        (journal.grid_consumption_high_kwh or 0)

    # Align data structure with frontend expectations
    setattr(journal, 'export_total_kwh', energy_flow_dict.get("total_grid_feed_in_kwh", 0))

    energy_flow = journal_schema.EnergyFlow(
        self_consumption_kwh=energy_flow_dict.get("self_consumption_kwh", 0),
        total_household_consumption_kwh=energy_flow_dict.get("total_household_consumption_kwh", 0),
        home_consumption_kwh=energy_flow_dict.get("home_consumption_kwh", 0),
        self_sufficiency_ratio=energy_flow_dict.get("self_sufficiency_ratio", 0),
        total_grid_feed_in_kwh=energy_flow_dict.get("total_grid_feed_in_kwh", 0),
        import_total_kwh=import_total_kwh
    )

    financial_statement = journal_schema.MonthlyStatement.model_validate(statement)

    # The frontend expects the raw journal data under the 'metric' key
    metric = journal_schema.MonthlyJournal.model_validate(journal)

    chart_data = journal_schema.FrontendChartData(
        metric=metric,
        financial_statement=financial_statement,
        energy_flow=energy_flow
    )
    return chart_data

@router.post("/", response_model=journal_schema.MonthlyJournal, status_code=status.HTTP_201_CREATED)
def create_new_journal(
    *,
    db: Session = Depends(get_db),
    journal_in: journal_schema.MonthlyJournalCreate,
    current_user: str = Depends(deps.get_current_user)
):
    """
    Create a new monthly journal entry.
    """
    # Check if a journal for this period already exists
    existing_journal = crud_journal.get_journal_by_year_and_month(db, year=journal_in.year, month=journal_in.month)
    if existing_journal:
        raise HTTPException(
            status_code=409,
            detail=f"A journal entry for {journal_in.year}-{journal_in.month} already exists. Use the PUT endpoint to update.",
        )
    journal = crud_journal.create_journal(db=db, obj_in=journal_in)
    return journal

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
    db_journals = crud_journal.get_journals_by_year(db, year=year)
    if not db_journals:
        return []

    return [_get_processed_journal_data(journal) for journal in db_journals]

@router.get("/{year}/{month}", response_model=journal_schema.FrontendChartData)
def read_journal_for_month(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Retrieve a single monthly journal entry, run calculations, and return
    the data in the format expected by the frontend.
    """
    db_journal = crud_journal.get_journal_by_year_and_month(db, year=year, month=month)
    if not db_journal:
        raise HTTPException(status_code=404, detail="Journal not found for this period.")

    return _get_processed_journal_data(db_journal)

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
