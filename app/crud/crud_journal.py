from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import models
from app.schemas import journal as journal_schema

def create_journal(db: Session, *, obj_in: journal_schema.MonthlyJournalCreate) -> models.MonthlyJournal:
    """
    Creates a new monthly journal record, including its associated car entries.
    """
    # Create the main journal object
    journal_data = obj_in.model_dump(exclude={"car_entries"})
    db_journal = models.MonthlyJournal(**journal_data)

    # Create the associated car journal entries
    car_entries_data = obj_in.car_entries
    db_car_entries = [models.CarJournalEntry(**entry.model_dump(), journal=db_journal) for entry in car_entries_data]

    db.add(db_journal)
    db.add_all(db_car_entries)
    db.commit()
    db.refresh(db_journal)
    return db_journal


def get_journal_by_year_and_month(db: Session, *, year: int, month: int) -> Optional[models.MonthlyJournal]:
    """
    Retrieves a single monthly journal by its year and month.
    """
    return db.query(models.MonthlyJournal).filter(models.MonthlyJournal.year == year, models.MonthlyJournal.month == month).first()


def get_journals(db: Session, skip: int = 0, limit: int = 100) -> List[models.MonthlyJournal]:
    """
    Retrieves multiple monthly journals with pagination.
    """
    return db.query(models.MonthlyJournal).order_by(models.MonthlyJournal.year.desc(), models.MonthlyJournal.month.desc()).offset(skip).limit(limit).all()


def remove_journal(db: Session, *, journal_id: int) -> Optional[models.MonthlyJournal]:
    """
    Removes a journal record and its associated car entries from the database.
    The 'delete-orphan' cascade on the relationship handles the car entries automatically.
    """
    db_obj = db.query(models.MonthlyJournal).filter(models.MonthlyJournal.id == journal_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


def get_or_create_journals_for_year(db: Session, *, year: int) -> List[models.MonthlyJournal]:
    """
    Retrieves all 12 monthly journals for a given year.
    If a journal for a specific month does not exist, it creates an empty one.
    """
    journals = []
    for month in range(1, 13):
        journal = get_journal_by_year_and_month(db, year=year, month=month)
        if not journal:
            journal_in = journal_schema.MonthlyJournalCreate(year=year, month=month)
            journal = create_journal(db=db, obj_in=journal_in)
        journals.append(journal)
    # Sort journals by month
    journals.sort(key=lambda j: j.month)
    return journals


def update_journal(db: Session, *, year: int, month: int, obj_in: journal_schema.MonthlyJournalBase) -> Optional[models.MonthlyJournal]:
    """
    Updates a monthly journal record.
    """
    journal = get_journal_by_year_and_month(db, year=year, month=month)
    if journal:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(journal, field, value)
        db.add(journal)
        db.commit()
        db.refresh(journal)
    return journal
