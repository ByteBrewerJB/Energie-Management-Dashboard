from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api import deps
from app.schemas import journal as journal_schema
from app.crud import crud_journal

router = APIRouter()


@router.get("/years", response_model=List[int])
def get_journal_years(
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Retrieve all unique years from journal entries.
    """
    return crud_journal.get_all_years(db=db)


@router.get("/{year}", response_model=List[journal_schema.MonthlyJournal])
def read_journals_by_year(
    year: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Retrieve journal entries for a specific year.
    """
    journals = crud_journal.get_by_year(db=db, year=year)
    return journals


@router.get("/", response_model=List[journal_schema.MonthlyJournal])
def read_journals(
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Retrieve the last 24 monthly journal entries, sorted chronologically.
    """
    journals = crud_journal.get_journals(db, limit=24)
    # Reverse the list to have the oldest month first
    return journals[::-1]

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
