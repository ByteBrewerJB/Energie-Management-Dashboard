from sqlalchemy.orm import Session
from app.models import models
from app.schemas import metrics as metrics_schema

def get_metric(db: Session, metric_id: int):
    return db.query(models.MonthlyMetric).filter(models.MonthlyMetric.id == metric_id).first()

def get_metrics(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MonthlyMetric).offset(skip).limit(limit).all()

def create_monthly_metric(db: Session, metric: metrics_schema.MonthlyMetricCreate) -> models.MonthlyMetric:
    """
    Creates a new monthly metric record in the database.
    """
    db_metric = models.MonthlyMetric(**metric.dict())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def update_metric(db: Session, metric_id: int, metric: metrics_schema.MonthlyMetricCreate):
    db_metric = db.query(models.MonthlyMetric).filter(models.MonthlyMetric.id == metric_id).first()
    if db_metric:
        for key, value in metric.dict().items():
            setattr(db_metric, key, value)
        db.commit()
        db.refresh(db_metric)
    return db_metric

def delete_metric(db: Session, metric_id: int):
    db_metric = db.query(models.MonthlyMetric).filter(models.MonthlyMetric.id == metric_id).first()
    if db_metric:
        db.delete(db_metric)
        db.commit()
    return db_metric
