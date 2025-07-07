from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import StudentScheduleDetail, StudentSchedule, Service
from ..schemas import StudentScheduleDetailCreate, StudentScheduleDetailBase
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context


class CRUDStudentScheduleDetail(CRUDBase[StudentScheduleDetail, StudentScheduleDetailCreate, StudentScheduleDetailBase]):
    def get_by_schedule(self, db: Session, *, schedule_id: str) -> List[StudentScheduleDetail]:
        return db.query(StudentScheduleDetail).filter(
            StudentScheduleDetail.schedule_id == schedule_id
        ).order_by(StudentScheduleDetail.ordre_service).all()

    def get_by_service(self, db: Session, *, service_id: str) -> List[StudentScheduleDetail]:
        return db.query(StudentScheduleDetail).filter(
            StudentScheduleDetail.service_id == service_id
        ).all()

    def create_with_validation(
        self, db: Session, *, obj_in: StudentScheduleDetailCreate
    ) -> StudentScheduleDetail:
        # Validate schedule exists
        schedule = db.query(StudentSchedule).filter(
            StudentSchedule.id == obj_in.schedule_id).first()
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planning étudiant non trouvé"
            )

        # Validate service exists if provided
        if obj_in.service_id:
            service = db.query(Service).filter(
                Service.id == obj_in.service_id).first()
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service non trouvé"
                )

        # Validate service name
        validate_string_length(obj_in.service_nom, "nom du service", 2, 200)

        # Validate status
        valid_statuses = ["planifie", "en_cours", "termine", "annule"]
        if obj_in.statut not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Statut invalide. Statuts valides: {', '.join(valid_statuses)}"
            )

        # Validate dates if provided
        if obj_in.date_debut and obj_in.date_fin:
            try:
                from datetime import datetime
                date_debut = datetime.strptime(obj_in.date_debut, "%Y-%m-%d")
                date_fin = datetime.strptime(obj_in.date_fin, "%Y-%m-%d")
                if date_debut >= date_fin:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La date de début doit être antérieure à la date de fin"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Format de date invalide. Utilisez YYYY-MM-DD"
                )

        # Check for duplicate service in same schedule
        existing_detail = db.query(StudentScheduleDetail).filter(
            StudentScheduleDetail.schedule_id == obj_in.schedule_id,
            StudentScheduleDetail.service_id == obj_in.service_id
        ).first()

        if existing_detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce service existe déjà dans ce planning"
            )

        db_detail = StudentScheduleDetail(
            id=str(uuid.uuid4()),
            schedule_id=obj_in.schedule_id,
            rotation_id=obj_in.rotation_id,
            service_id=obj_in.service_id,
            service_nom=obj_in.service_nom,
            ordre_service=obj_in.ordre_service,
            date_debut=obj_in.date_debut,
            date_fin=obj_in.date_fin,
            duree_jours=obj_in.duree_jours,
            statut=obj_in.statut,
            notes=obj_in.notes
        )

        try:
            db.add(db_detail)
            db.commit()
            db.refresh(db_detail)
            return db_detail
        except Exception as e:
            handle_unique_constraint(e, "Le détail du planning")

    def update_with_validation(
        self, db: Session, *, db_obj: StudentScheduleDetail, obj_in: StudentScheduleDetailCreate
    ) -> StudentScheduleDetail:
        # Validate service exists if being changed
        if obj_in.service_id and obj_in.service_id != db_obj.service_id:
            service = db.query(Service).filter(
                Service.id == obj_in.service_id).first()
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service non trouvé"
                )

        # Validate service name
        validate_string_length(obj_in.service_nom, "nom du service", 2, 200)

        # Validate status
        valid_statuses = ["planifie", "en_cours", "termine", "annule"]
        if obj_in.statut not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Statut invalide. Statuts valides: {', '.join(valid_statuses)}"
            )

        # Validate dates if provided
        if obj_in.date_debut and obj_in.date_fin:
            try:
                from datetime import datetime
                date_debut = datetime.strptime(obj_in.date_debut, "%Y-%m-%d")
                date_fin = datetime.strptime(obj_in.date_fin, "%Y-%m-%d")
                if date_debut >= date_fin:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La date de début doit être antérieure à la date de fin"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Format de date invalide. Utilisez YYYY-MM-DD"
                )

        # Check for duplicate service (excluding current detail)
        existing_detail = db.query(StudentScheduleDetail).filter(
            StudentScheduleDetail.schedule_id == obj_in.schedule_id,
            StudentScheduleDetail.service_id == obj_in.service_id,
            StudentScheduleDetail.id != db_obj.id
        ).first()

        if existing_detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce service existe déjà dans ce planning"
            )

        try:
            for field, value in obj_in.dict(exclude_unset=True).items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            handle_unique_constraint(e, "Le détail du planning")


student_schedule_detail = CRUDStudentScheduleDetail(StudentScheduleDetail)
