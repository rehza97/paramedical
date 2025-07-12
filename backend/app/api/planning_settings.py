from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import PlanningSettings
from ..schemas import PlanningSettingsCreate, PlanningSettingsUpdate, PlanningSettings as PlanningSettingsResponse

router = APIRouter()


@router.get("/", response_model=PlanningSettingsResponse)
def get_planning_settings(db: Session = Depends(get_db)):
    """Get current planning settings"""
    settings = db.query(PlanningSettings).first()
    if not settings:
        # Create default settings if none exist
        settings = PlanningSettings(
            academic_year_start="2025-01-01",
            total_duration_months=6,
            max_concurrent_students=2,
            break_days_between_rotations=2
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/", response_model=PlanningSettingsResponse)
def update_planning_settings(
    settings_update: PlanningSettingsUpdate,
    db: Session = Depends(get_db)
):
    """Update planning settings"""
    settings = db.query(PlanningSettings).first()
    if not settings:
        # Create new settings if none exist
        settings = PlanningSettings()
        db.add(settings)

    # Update fields
    if settings_update.academic_year_start is not None:
        settings.academic_year_start = settings_update.academic_year_start
    if settings_update.total_duration_months is not None:
        settings.total_duration_months = settings_update.total_duration_months
    if settings_update.max_concurrent_students is not None:
        settings.max_concurrent_students = settings_update.max_concurrent_students
    if settings_update.break_days_between_rotations is not None:
        settings.break_days_between_rotations = settings_update.break_days_between_rotations

    db.commit()
    db.refresh(settings)
    return settings


@router.post("/", response_model=PlanningSettingsResponse)
def create_planning_settings(
    settings_create: PlanningSettingsCreate,
    db: Session = Depends(get_db)
):
    """Create new planning settings"""
    # Check if settings already exist
    existing_settings = db.query(PlanningSettings).first()
    if existing_settings:
        raise HTTPException(
            status_code=400, detail="Planning settings already exist. Use PUT to update.")

    settings = PlanningSettings(**settings_create.model_dump())
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
