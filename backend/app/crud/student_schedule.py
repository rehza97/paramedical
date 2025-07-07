from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
import uuid
from datetime import datetime, timedelta
import json

from .base import CRUDBase
from ..models import StudentSchedule, StudentScheduleDetail, Etudiant, Planning, Service
from ..schemas import (
    StudentScheduleCreate,
    StudentScheduleBase,
    StudentScheduleDetailCreate,
    StudentScheduleSummary,
    StudentScheduleProgress
)
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context


class CRUDStudentSchedule(CRUDBase[StudentSchedule, StudentScheduleCreate, StudentScheduleBase]):

    def create_from_planning(
        self,
        db: Session,
        *,
        planning_id: str,
        etudiant_id: str,
        rotations: List[Dict],
        date_debut_planning: str,
        date_fin_planning: str
    ) -> StudentSchedule:
        """Create a student schedule from planning rotations"""

        try:
            # Validate inputs
            if not rotations:
                raise HTTPException(
                    status_code=400,
                    detail="Au moins une rotation doit être fournie"
                )

            # Parse dates safely
            try:
                date_debut = datetime.strptime(date_debut_planning, "%Y-%m-%d")
                date_fin = datetime.strptime(date_fin_planning, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Format de date invalide. Utilisez YYYY-MM-DD"
                )

            # Calculate schedule metrics
            nb_services_total = len(rotations)
            duree_totale_jours = (date_fin - date_debut).days + 1

            # Create the main schedule
            db_schedule = StudentSchedule(
                id=str(uuid.uuid4()),
                etudiant_id=etudiant_id,
                planning_id=planning_id,
                date_debut_planning=date_debut_planning,
                date_fin_planning=date_fin_planning,
                nb_services_total=nb_services_total,
                duree_totale_jours=duree_totale_jours,
                statut="en_cours",
                nb_services_completes=0  # Initialize to 0
            )
            db.add(db_schedule)
            db.flush()

            # Create schedule details for each rotation
            for rotation_data in rotations:
                try:
                    date_debut_rotation = datetime.strptime(
                        rotation_data['date_debut'], "%Y-%m-%d")
                    date_fin_rotation = datetime.strptime(
                        rotation_data['date_fin'], "%Y-%m-%d")
                    duree_jours = (date_fin_rotation -
                                   date_debut_rotation).days + 1
                except (ValueError, KeyError) as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Données de rotation invalides: {str(e)}"
                    )

                schedule_detail = StudentScheduleDetail(
                    id=str(uuid.uuid4()),
                    schedule_id=db_schedule.id,
                    rotation_id=rotation_data.get('id'),
                    service_id=rotation_data.get('service_id'),
                    service_nom=rotation_data.get('service_nom'),
                    ordre_service=rotation_data.get('ordre'),
                    date_debut=rotation_data['date_debut'],
                    date_fin=rotation_data['date_fin'],
                    duree_jours=duree_jours,
                    statut="planifie"
                )
                db.add(schedule_detail)

            db.commit()
            db.refresh(db_schedule)
            return db_schedule

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la création du planning: {str(e)}"
            )

    def get_by_etudiant(self, db: Session, *, etudiant_id: str) -> List[StudentSchedule]:
        """Get all schedules for a student"""
        return db.query(StudentSchedule).filter(
            StudentSchedule.etudiant_id == etudiant_id
        ).order_by(StudentSchedule.date_creation.desc()).all()

    def get_active_by_etudiant(self, db: Session, *, etudiant_id: str) -> Optional[StudentSchedule]:
        """Get the active schedule for a student"""
        return db.query(StudentSchedule).filter(
            StudentSchedule.etudiant_id == etudiant_id,
            StudentSchedule.is_active == True
        ).first()

    def get_by_planning(self, db: Session, *, planning_id: str) -> List[StudentSchedule]:
        """Get all schedules for a planning"""
        return db.query(StudentSchedule).filter(
            StudentSchedule.planning_id == planning_id
        ).all()

    def update_progress(
        self,
        db: Session,
        *,
        schedule_id: str,
        service_id: str,
        new_statut: str,
        notes: Optional[str] = None
    ) -> StudentScheduleDetail:
        """Update the progress of a specific service in a schedule"""

        try:
            # Validate status
            valid_statuses = ["planifie", "en_cours", "termine", "annule"]
            if new_statut not in valid_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=f"Statut invalide. Statuts valides: {', '.join(valid_statuses)}"
                )

            # Find the schedule detail
            schedule_detail = db.query(StudentScheduleDetail).filter(
                StudentScheduleDetail.schedule_id == schedule_id,
                StudentScheduleDetail.service_id == service_id
            ).first()

            if not schedule_detail:
                raise HTTPException(
                    status_code=404,
                    detail="Service non trouvé dans le planning"
                )

            # Update status and notes
            schedule_detail.statut = new_statut
            if notes:
                schedule_detail.notes = notes

            # Update actual dates if service is starting/completing
            current_date = datetime.now().strftime("%Y-%m-%d")
            if new_statut == "en_cours" and not schedule_detail.date_debut_reelle:
                schedule_detail.date_debut_reelle = current_date
            elif new_statut == "termine" and not schedule_detail.date_fin_reelle:
                schedule_detail.date_fin_reelle = current_date

            # Update the main schedule completion count
            schedule = db.query(StudentSchedule).filter(
                StudentSchedule.id == schedule_id
            ).first()

            if schedule:
                completed_services = db.query(StudentScheduleDetail).filter(
                    StudentScheduleDetail.schedule_id == schedule_id,
                    StudentScheduleDetail.statut == "termine"
                ).count()

                schedule.nb_services_completes = completed_services
                schedule.date_modification = datetime.now()

                # Update overall status if all services are completed
                if completed_services == schedule.nb_services_total:
                    schedule.statut = "termine"

            db.commit()
            db.refresh(schedule_detail)
            return schedule_detail

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la mise à jour: {str(e)}"
            )

    def get_progress_summary(self, db: Session, *, etudiant_id: str) -> StudentScheduleProgress:
        """Get a comprehensive progress summary for a student"""

        # Get active schedule
        schedule = self.get_active_by_etudiant(db, etudiant_id=etudiant_id)
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Aucun planning actif trouvé"
            )

        # Get student info
        etudiant = db.query(Etudiant).filter(
            Etudiant.id == etudiant_id).first()
        if not etudiant:
            raise HTTPException(
                status_code=404,
                detail="Étudiant non trouvé"
            )

        # Get all schedule details
        details = db.query(StudentScheduleDetail).filter(
            StudentScheduleDetail.schedule_id == schedule.id
        ).order_by(StudentScheduleDetail.ordre_service).all()

        # Categorize services
        services_completes = []
        services_en_cours = []
        services_planifies = []
        prochaine_service = None
        date_prochaine_service = None

        current_date = datetime.now().date()

        for detail in details:
            service_name = detail.service_nom
            if detail.statut == "termine":
                services_completes.append(service_name)
            elif detail.statut == "en_cours":
                services_en_cours.append(service_name)
            elif detail.statut == "planifie":
                services_planifies.append(service_name)
                # Find the next planned service
                try:
                    detail_date = datetime.strptime(
                        detail.date_debut, "%Y-%m-%d").date()
                    if not prochaine_service and detail_date >= current_date:
                        prochaine_service = service_name
                        date_prochaine_service = detail.date_debut
                except ValueError:
                    # Skip if date format is invalid
                    continue

        # Calculate global progression - handle division by zero
        if schedule.nb_services_total > 0:
            progression_globale = (
                len(services_completes) / schedule.nb_services_total) * 100
        else:
            progression_globale = 0.0

        return StudentScheduleProgress(
            etudiant_id=etudiant_id,
            etudiant_nom=f"{etudiant.prenom} {etudiant.nom}",
            services_completes=services_completes,
            services_en_cours=services_en_cours,
            services_planifies=services_planifies,
            progression_globale=round(progression_globale, 1),
            prochaine_service=prochaine_service,
            date_prochaine_service=date_prochaine_service
        )

    def get_summary_by_planning(self, db: Session, *, planning_id: str) -> List[StudentScheduleSummary]:
        """Get summary of all student schedules in a planning"""

        # Use a single query with join for better performance
        query = db.query(StudentSchedule, Etudiant).join(
            Etudiant, StudentSchedule.etudiant_id == Etudiant.id
        ).filter(StudentSchedule.planning_id == planning_id)

        results = query.all()
        summaries = []

        for schedule, etudiant in results:
            # Calculate progression - handle division by zero
            if schedule.nb_services_total > 0:
                progression = (schedule.nb_services_completes /
                               schedule.nb_services_total) * 100
            else:
                progression = 0.0

            summary = StudentScheduleSummary(
                id=schedule.id,
                etudiant_id=schedule.etudiant_id,
                etudiant_nom=f"{etudiant.prenom} {etudiant.nom}",
                planning_id=schedule.planning_id,
                date_debut_planning=schedule.date_debut_planning,
                date_fin_planning=schedule.date_fin_planning,
                nb_services_total=schedule.nb_services_total,
                nb_services_completes=schedule.nb_services_completes,
                duree_totale_jours=schedule.duree_totale_jours,
                statut=schedule.statut,
                progression=round(progression, 1)
            )
            summaries.append(summary)

        return summaries

    def archive_schedule(self, db: Session, *, schedule_id: str) -> StudentSchedule:
        """Archive a schedule (mark as inactive)"""
        try:
            schedule = self.get(db, id=schedule_id)
            if not schedule:
                raise HTTPException(
                    status_code=404,
                    detail="Planning non trouvé"
                )

            schedule.is_active = False
            schedule.date_modification = datetime.now()
            db.commit()
            db.refresh(schedule)
            return schedule

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'archivage: {str(e)}"
            )

    def create_new_version(self, db: Session, *, schedule_id: str) -> StudentSchedule:
        """Create a new version of an existing schedule"""
        try:
            old_schedule = self.get(db, id=schedule_id)
            if not old_schedule:
                raise HTTPException(
                    status_code=404,
                    detail="Planning non trouvé"
                )

            # Archive old schedule
            self.archive_schedule(db, schedule_id=schedule_id)

            # Create new version
            new_schedule = StudentSchedule(
                id=str(uuid.uuid4()),
                etudiant_id=old_schedule.etudiant_id,
                planning_id=old_schedule.planning_id,
                date_debut_planning=old_schedule.date_debut_planning,
                date_fin_planning=old_schedule.date_fin_planning,
                nb_services_total=old_schedule.nb_services_total,
                nb_services_completes=old_schedule.nb_services_completes,
                duree_totale_jours=old_schedule.duree_totale_jours,
                taux_occupation_moyen=old_schedule.taux_occupation_moyen,
                statut=old_schedule.statut,
                version=old_schedule.version + 1 if old_schedule.version else 1,
                is_active=True
            )
            db.add(new_schedule)
            db.flush()

            # Copy schedule details
            old_details = db.query(StudentScheduleDetail).filter(
                StudentScheduleDetail.schedule_id == schedule_id
            ).all()

            for old_detail in old_details:
                new_detail = StudentScheduleDetail(
                    id=str(uuid.uuid4()),
                    schedule_id=new_schedule.id,
                    rotation_id=old_detail.rotation_id,
                    service_id=old_detail.service_id,
                    service_nom=old_detail.service_nom,
                    ordre_service=old_detail.ordre_service,
                    date_debut=old_detail.date_debut,
                    date_fin=old_detail.date_fin,
                    duree_jours=old_detail.duree_jours,
                    statut=old_detail.statut,
                    date_debut_reelle=old_detail.date_debut_reelle,
                    date_fin_reelle=old_detail.date_fin_reelle,
                    notes=old_detail.notes,
                    modifications=old_detail.modifications
                )
                db.add(new_detail)

            db.commit()
            db.refresh(new_schedule)
            return new_schedule

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la création de la nouvelle version: {str(e)}"
            )


student_schedule = CRUDStudentSchedule(StudentSchedule)
