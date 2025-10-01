from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, get_db_session
from ..models.car_charge_journal import CarChargeJournal
from ..models.monthly_journal import MonthlyJournal
from ..models.user import User
from ..schemas.monthly_journal import (
    MonthlyJournalCreate,
    MonthlyJournalRead,
    MonthlyJournalUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[MonthlyJournalRead])
def list_journals(
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> List[MonthlyJournal]:
    query = db.query(MonthlyJournal).filter(MonthlyJournal.owner_id == current_user.id)
    if year is not None:
        query = query.filter(MonthlyJournal.year == year)
    return query.order_by(MonthlyJournal.year.desc(), MonthlyJournal.month.desc()).all()


@router.get("/{journal_id}", response_model=MonthlyJournalRead)
def get_journal(
    journal_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> MonthlyJournal:
    journal = (
        db.query(MonthlyJournal)
        .filter(MonthlyJournal.id == journal_id, MonthlyJournal.owner_id == current_user.id)
        .first()
    )
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journaal niet gevonden")
    return journal


@router.post("/", response_model=MonthlyJournalRead, status_code=status.HTTP_201_CREATED)
def create_journal(
    journal_in: MonthlyJournalCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> MonthlyJournal:
    existing = (
        db.query(MonthlyJournal)
        .filter(
            MonthlyJournal.owner_id == current_user.id,
            MonthlyJournal.year == journal_in.year,
            MonthlyJournal.month == journal_in.month,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Journaal voor deze maand bestaat al")

    journal = MonthlyJournal(owner_id=current_user.id, **journal_in.model_dump(exclude={"car_charges"}))
    db.add(journal)
    db.flush()

    for charge_in in journal_in.car_charges:
        charge = CarChargeJournal(
            journal_id=journal.id,
            car_id=charge_in.car_id,
            charged_kwh=charge_in.charged_kwh,
        )
        db.add(charge)

    db.commit()
    db.refresh(journal)
    return journal


@router.put("/{journal_id}", response_model=MonthlyJournalRead)
def update_journal(
    journal_id: int,
    journal_in: MonthlyJournalUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> MonthlyJournal:
    journal = (
        db.query(MonthlyJournal)
        .filter(MonthlyJournal.id == journal_id, MonthlyJournal.owner_id == current_user.id)
        .first()
    )
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journaal niet gevonden")

    update_data = journal_in.model_dump(exclude_unset=True, exclude={"car_charges"})
    for field, value in update_data.items():
        setattr(journal, field, value)

    if journal_in.car_charges is not None:
        db.query(CarChargeJournal).filter(CarChargeJournal.journal_id == journal.id).delete()
        for charge_in in journal_in.car_charges:
            db.add(
                CarChargeJournal(
                    journal_id=journal.id,
                    car_id=charge_in.car_id,
                    charged_kwh=charge_in.charged_kwh,
                )
            )

    db.commit()
    db.refresh(journal)
    return journal


@router.delete("/{journal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal(
    journal_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    journal = (
        db.query(MonthlyJournal)
        .filter(MonthlyJournal.id == journal_id, MonthlyJournal.owner_id == current_user.id)
        .first()
    )
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journaal niet gevonden")

    db.delete(journal)
    db.commit()
