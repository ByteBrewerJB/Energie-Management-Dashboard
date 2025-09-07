from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api import deps
from app.schemas import journal as journal_schema
from app.crud import crud_journal
from app.services import financial_calculations

router = APIRouter()

@router.post("/", response_model=journal_schema.MonthlyJournal)
def create_monthly_journal(
    *,
    db: Session = Depends(get_db),
    journal_in: journal_schema.MonthlyJournalCreate,
    current_user: str = Depends(deps.get_current_user)
):
    """
    Create a new monthly journal entry.
    This is the primary endpoint for submitting monthly data.
    """
    # Check if a journal for this month already exists
    existing_journal = crud_journal.get_journal_by_year_and_month(
        db, year=journal_in.year, month=journal_in.month
    )
    if existing_journal:
        raise HTTPException(
            status_code=409,
            detail="A journal entry for this year and month already exists.",
        )

    journal = crud_journal.create_journal(db=db, obj_in=journal_in)
    return journal

@router.get("/", response_model=List[journal_schema.MonthlyJournal])
def read_journals(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(deps.get_current_user)
):
    """
    Retrieve all monthly journal entries, sorted by most recent.
    """
    journals = crud_journal.get_journals(db, skip=skip, limit=limit)
    return journals

@router.get("/{year}/{month}", response_model=journal_schema.JournalWithStatement)
def read_journal_with_statement(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Retrieve a single monthly journal by year and month, including the
    calculated financial statement.
    """
    journal = crud_journal.get_journal_by_year_and_month(db, year=year, month=month)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found for this period.")

    statement = financial_calculations.calculate_monthly_statement(journal)

    return journal_schema.JournalWithStatement(
        journal_data=journal,
        financial_statement=statement
    )

@router.delete("/{journal_id}", response_model=journal_schema.MonthlyJournal)
def delete_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Delete a monthly journal entry.
    """
    journal = crud_journal.remove_journal(db=db, journal_id=journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found.")
    return journal
