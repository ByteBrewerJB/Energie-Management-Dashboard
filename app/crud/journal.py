from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.journal import MonthlyJournal, CarJournalEntry
from app.schemas.journal import MonthlyJournalCreate, MonthlyJournalUpdate


def get_journal(db: Session, year: int, month: int) -> Optional[MonthlyJournal]:
    return db.query(MonthlyJournal).filter(MonthlyJournal.year == year, MonthlyJournal.month == month).first()


def get_journals_by_year(db: Session, year: int) -> List[MonthlyJournal]:
    return db.query(MonthlyJournal).filter(MonthlyJournal.year == year).order_by(MonthlyJournal.month).all()


def create_or_update_journal(db: Session, journal_in: MonthlyJournalCreate) -> MonthlyJournal:
    db_journal = get_journal(db, year=journal_in.year, month=journal_in.month)

    if db_journal:
        # Update existing journal
        update_data = journal_in.model_dump(exclude_unset=True)
        # Handle nested car entries separately
        car_entries_data = update_data.pop("car_journal_entries", [])

        for key, value in update_data.items():
            setattr(db_journal, key, value)

        # Clear existing car entries and add new ones
        # This is a simple approach. A more sophisticated one might update existing entries.
        db.query(CarJournalEntry).filter(CarJournalEntry.monthly_journal_id == db_journal.id).delete()

        for car_entry_data in car_entries_data:
            db_car_entry = CarJournalEntry(
                **car_entry_data.model_dump(),
                monthly_journal_id=db_journal.id
            )
            db.add(db_car_entry)

        db.commit()
        db.refresh(db_journal)
        return db_journal

    else:
        # Create new journal
        car_entries_data = journal_in.car_journal_entries
        journal_data = journal_in.model_dump()
        del journal_data["car_journal_entries"]

        db_journal = MonthlyJournal(**journal_data)
        db.add(db_journal)
        db.commit() # Commit to get the ID for the journal
        db.refresh(db_journal)

        for car_entry_data in car_entries_data:
            db_car_entry = CarJournalEntry(
                **car_entry_data.model_dump(),
                monthly_journal_id=db_journal.id
            )
            db.add(db_car_entry)

        db.commit()
        db.refresh(db_journal)
        return db_journal
