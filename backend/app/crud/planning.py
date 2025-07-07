from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid
from datetime import datetime, timedelta

from .base import CRUDBase
from ..models import Planning, Promotion, Service, Rotation, Etudiant, PromotionYear
from ..schemas import PlanningCreate, PlanningBase
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context
from .planning_settings import planning_settings


class CRUDPlanning(CRUDBase[Planning, PlanningCreate, PlanningBase]):
    def get_by_promotion(self, db: Session, *, promo_id: str) -> Optional[Planning]:
        """Get planning for a promotion"""
        return db.query(Planning).filter(Planning.promo_id == promo_id).first()

    def generate_planning(
        self, db: Session, *, promo_id: str, date_debut: str = None
    ) -> Planning:
        """Generate optimized planning for a promotion using planning settings"""
        # Get planning settings
        settings = planning_settings.get_or_create_default(db)

        # Use settings start date if not provided
        if not date_debut:
            date_debut = settings.academic_year_start

        promotion = db.query(Promotion).filter(
            Promotion.id == promo_id).first()
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion non trouvée"
            )

        # Get students (only active ones)
        etudiants = db.query(Etudiant).filter(
            Etudiant.promotion_id == promo_id,
            Etudiant.is_active == True
        ).all()
        if not etudiants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun étudiant actif dans cette promotion"
            )

        # Get active promotion year and its services
        active_year = db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promo_id,
            PromotionYear.is_active == True
        ).first()

        if not active_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucune année active trouvée pour cette promotion"
            )

        # Get services assigned to the active year
        services = active_year.services
        if not services:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun service configuré pour cette année"
            )

        # Clear existing planning properly
        existing_planning = self.get_by_promotion(db, promo_id=promo_id)
        if existing_planning:
            # Delete in correct order to avoid foreign key violations:
            # 1. Delete student schedule details first
            # 2. Delete student schedules
            # 3. Delete rotations
            # 4. Delete planning

            from ..models import StudentSchedule, StudentScheduleDetail

            # Get all student schedules for this planning
            student_schedules = db.query(StudentSchedule).filter(
                StudentSchedule.planning_id == existing_planning.id).all()

            # Delete student schedule details first
            for schedule in student_schedules:
                db.query(StudentScheduleDetail).filter(
                    StudentScheduleDetail.schedule_id == schedule.id).delete()

            # Delete student schedules
            db.query(StudentSchedule).filter(
                StudentSchedule.planning_id == existing_planning.id).delete()

            # Now delete rotations
            db.query(Rotation).filter(Rotation.planning_id ==
                                      existing_planning.id).delete()

            # Finally delete the planning
            db.delete(existing_planning)
            db.flush()  # Ensure deletion is committed before creating new planning

        # Create new planning
        db_planning = Planning(
            id=str(uuid.uuid4()),
            promo_id=promo_id,
            promotion_year_id=active_year.id,
            annee_niveau=active_year.annee_niveau
        )
        db.add(db_planning)
        db.flush()

        # Calculate planning constraints
        nb_etudiants = len(etudiants)
        nb_services = len(services)
        date_debut_dt = datetime.strptime(date_debut, "%Y-%m-%d")

        # Calculate total duration limit based on settings
        total_duration_days = settings.total_duration_months * 30  # Approximate
        date_fin_limite = date_debut_dt + timedelta(days=total_duration_days)

        # Calculate optimal service selection per student
        # Instead of all services, select a reasonable subset
        total_service_days = sum(
            service.duree_stage_jours for service in services)

        # If all services exceed duration limit, select priority services
        if total_service_days > total_duration_days:
            # Sort services by priority (shortest first for better distribution)
            services_sorted = sorted(
                services, key=lambda x: x.duree_stage_jours)
            selected_services = []
            current_days = 0

            for service in services_sorted:
                if current_days + service.duree_stage_jours <= total_duration_days:
                    selected_services.append(service)
                    current_days += service.duree_stage_jours
                else:
                    break

            services = selected_services
        nb_services = len(services)

        if nb_services == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun service ne peut être planifié dans la durée limite"
            )

        # Initialize tracking variables
        rotations = []
        service_occupation = {}
        student_completed_services = {}
        student_next_available_date = {}

        for etudiant in etudiants:
            student_completed_services[etudiant.id] = set()
            student_next_available_date[etudiant.id] = date_debut_dt

        # Optimized planning algorithm
        max_iterations = nb_etudiants * nb_services
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            progress_made = False

            for etudiant in etudiants:
                # Check if student has completed all selected services
                if len(student_completed_services[etudiant.id]) >= nb_services:
                    continue

                # Check if student would exceed duration limit
                current_date = student_next_available_date[etudiant.id]
                if current_date >= date_fin_limite:
                    continue

                # Find best available service
                best_assignment = None
                best_score = -1

                for service in services:
                    if service.id in student_completed_services[etudiant.id]:
                        continue

                    # Check if service fits within duration limit
                    service_end_date = current_date + \
                        timedelta(days=service.duree_stage_jours - 1)
                    if service_end_date > date_fin_limite:
                        continue

                    # Check service availability
                    service_id = service.id
                    if service_id not in service_occupation:
                        service_occupation[service_id] = {}

                    date_str = current_date.strftime("%Y-%m-%d")
                    if date_str not in service_occupation[service_id]:
                        service_occupation[service_id][date_str] = 0

                    # Use planning settings for max concurrent students
                    max_concurrent = min(
                        service.places_disponibles, settings.max_concurrent_students)

                    if service_occupation[service_id][date_str] < max_concurrent:
                        # Calculate score based on availability and priority
                        availability_score = (
                            max_concurrent - service_occupation[service_id][date_str]) / max_concurrent
                        # Prefer shorter services for better distribution
                        priority_score = 1.0 / service.duree_stage_jours
                        score = availability_score * 0.7 + priority_score * 0.3

                        if score > best_score:
                            best_score = score
                            best_assignment = {
                                'service': service,
                                'start_date': current_date,
                                'end_date': service_end_date,
                                'order': len(rotations) + 1
                            }

                # Create rotation if assignment found
                if best_assignment:
                    rotation = Rotation(
                        id=str(uuid.uuid4()),
                        etudiant_id=etudiant.id,
                        service_id=best_assignment['service'].id,
                        date_debut=best_assignment['start_date'].strftime(
                            "%Y-%m-%d"),
                        date_fin=best_assignment['end_date'].strftime(
                            "%Y-%m-%d"),
                        ordre=best_assignment['order'],
                        planning_id=db_planning.id
                    )
                    rotations.append(rotation)
                    db.add(rotation)

                    # Update tracking
                    student_completed_services[etudiant.id].add(
                        best_assignment['service'].id)
                    student_next_available_date[etudiant.id] = best_assignment['end_date'] + timedelta(
                        days=settings.break_days_between_rotations)

                    # Update service occupation
                    current_date = best_assignment['start_date']
                    while current_date <= best_assignment['end_date']:
                        date_str = current_date.strftime("%Y-%m-%d")
                        if date_str not in service_occupation[best_assignment['service'].id]:
                            service_occupation[best_assignment['service'].id][date_str] = 0
                        service_occupation[best_assignment['service'].id][date_str] += 1
                        current_date += timedelta(days=1)

                    progress_made = True

            # Exit if no progress made
            if not progress_made:
                break

        # Commit the planning
        try:
            db.commit()
            db.refresh(db_planning)
            return db_planning
        except Exception as e:
            handle_unique_constraint(e, "Le planning")

    def get_student_planning(
        self, db: Session, *, promo_id: str, etudiant_id: str
    ) -> List[Rotation]:
        """Get planning for a specific student"""
        planning = self.get_by_promotion(db, promo_id=promo_id)
        if not planning:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planning non trouvé"
            )
        rotations = db.query(Rotation).filter(
            Rotation.planning_id == planning.id,
            Rotation.etudiant_id == etudiant_id
        ).order_by(Rotation.ordre).all()
        return rotations


planning = CRUDPlanning(Planning)
