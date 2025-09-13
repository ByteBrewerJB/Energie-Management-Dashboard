from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.journal import MonthlyJournal, MonthlyJournalCreate
from app.services import journal_service
from app.models.user import User

router = APIRouter()


@router.put("/{year}/{month}", response_model=MonthlyJournal)
def create_or_update_journal_entry(
    year: int,
    month: int,
    journal_in: MonthlyJournalCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create or update a monthly journal entry.
    """
    # Ensure the path year/month match the payload
    if journal_in.year != year or journal_in.month != month:
        raise HTTPException(
            status_code=400,
            detail="The year and month in the URL path do not match the payload.",
        )

    db_journal = crud.journal.create_or_update_journal(db=db, journal_in=journal_in)
    return journal_service.process_journal_entry(db, db_journal)


@router.get("/{year}", response_model=List[MonthlyJournal])
def read_journal_for_year(
    year: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve all processed monthly journal entries for a specific year.
    """
    db_journals = crud.journal.get_journals_by_year(db, year=year)
    if not db_journals:
        raise HTTPException(status_code=404, detail=f"No journal entries found for year {year}")

    return [journal_service.process_journal_entry(db, j) for j in db_journals]
