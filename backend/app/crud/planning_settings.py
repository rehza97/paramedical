from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .base import CRUDBase
from ..models import PlanningSettings
from ..schemas import PlanningSettingsCreate, PlanningSettingsUpdate
from .utils import handle_db_commit, handle_unique_constraint


class CRUDPlanningSettings(CRUDBase[PlanningSettings, PlanningSettingsCreate, PlanningSettingsUpdate]):
    def get_active_settings(self, db: Session) -> Optional[PlanningSettings]:
        """Get the active planning settings"""
        return db.query(PlanningSettings).filter(
            PlanningSettings.is_active == True
        ).first()

    def get_or_create_default(self, db: Session) -> PlanningSettings:
        """Get active settings or create default ones if none exist"""
        settings = self.get_active_settings(db)
        if not settings:
            # Create default settings
            default_settings = PlanningSettingsCreate(
                academic_year_start="2025-01-01",
                total_duration_months=6,
                max_concurrent_students=2,
                break_days_between_rotations=2,
                is_active=True
            )
            settings = self.create(db, obj_in=default_settings)
        return settings

    def update_settings(self, db: Session, *, obj_in: PlanningSettingsUpdate) -> PlanningSettings:
        """Update the active planning settings"""
        settings = self.get_active_settings(db)
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucune configuration de planification trouvée"
            )

        # Update the settings
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        try:
            db.commit()
            db.refresh(settings)
            return settings
        except Exception as e:
            handle_unique_constraint(e, "La configuration")

    def create_or_update(self, db: Session, *, obj_in: PlanningSettingsCreate) -> PlanningSettings:
        """Create new settings or update existing ones"""
        # Deactivate all existing settings
        db.query(PlanningSettings).update({"is_active": False})

        # Create new active settings
        settings = self.create(db, obj_in=obj_in)
        return settings


planning_settings = CRUDPlanningSettings(PlanningSettings)
