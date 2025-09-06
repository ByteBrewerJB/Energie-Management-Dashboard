from sqlalchemy.orm import Session
from app.models.models import MonthlyMetric
from app.schemas.metrics import MonthlyMetricCreate

def create_monthly_metric(db: Session, metric: MonthlyMetricCreate) -> MonthlyMetric:
    """
    Creates a new monthly metric record in the database.
    """
    db_metric = MonthlyMetric(**metric.dict())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric
