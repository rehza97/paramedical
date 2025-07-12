from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

from ..models import Planning, Promotion, Service, Rotation, Etudiant
from ..schemas import (
    PlanningEfficiencyAnalysis,
    PlanningValidationResult,
    ServiceOccupationStats,
    Planning as PlanningSchema,
    Rotation as RotationSchema
)


@dataclass
class ServiceScore:
    """Data class for service scoring"""
    service: Dict
    score: float
    available_date: datetime


class AdvancedPlanningAlgorithm:
    """Advanced planning algorithm with intelligent load balancing and optimization"""

    def __init__(self, db: Session):
        self.db = db
        self.service_occupation = defaultdict(lambda: defaultdict(int))
        self.student_completed_services = defaultdict(set)
        self.student_next_available_date = {}

    def generate_advanced_planning(
        self, promo_id: str, date_debut_str: str = "2025-01-01"
    ) -> Tuple[PlanningSchema, PlanningEfficiencyAnalysis, PlanningValidationResult]:
        """
        Generate planning using the advanced algorithm with efficiency analysis and validation
        """
        # Get promotion and services
        promotion = self._get_promotion(promo_id)
        services = self._get_services()

        # Convert to dict format for algorithm
        promotion_dict = self._convert_promotion_to_dict(promotion)
        services_list = self._convert_services_to_list(services)

        # Clear existing planning
        self._clear_existing_planning(promo_id)

        # Reset internal state
        self._reset_algorithm_state(
            promotion_dict['etudiants'], date_debut_str)

        # Generate planning using advanced algorithm
        planning_result = self._generate_optimized_planning(
            promotion_dict, services_list, date_debut_str
        )

        # Save to database
        db_planning = self._save_planning_to_db(planning_result)

        # Create student schedules
        self._create_student_schedules(db_planning, planning_result)

        # Analyze efficiency and validate
        efficiency_analysis = self._analyze_planning_efficiency(
            planning_result, services_list)
        validation_result = self._validate_planning(
            planning_result, services_list)

        # Convert to response format
        planning_response = self._convert_to_planning_response(db_planning)

        return planning_response, efficiency_analysis, validation_result

    def _get_promotion(self, promo_id: str) -> Promotion:
        """Get promotion from database"""
        promotion = self.db.query(Promotion).filter(
            Promotion.id == promo_id).first()
        if not promotion:
            raise HTTPException(
                status_code=404, detail="Promotion non trouvée")
        return promotion

    def _get_services(self) -> List[Service]:
        """Get all services from database"""
        services = self.db.query(Service).all()
        if not services:
            raise HTTPException(
                status_code=400, detail="Aucun service configuré")
        return services

    def _convert_promotion_to_dict(self, promotion: Promotion) -> Dict:
        """Convert promotion to dictionary format"""
        return {
            'id': promotion.id,
            'nom': promotion.nom,
            'etudiants': [
                {
                    'id': e.id,
                    'nom': e.nom,
                    'prenom': e.prenom
                } for e in promotion.etudiants
            ]
        }

    def _convert_services_to_list(self, services: List[Service]) -> List[Dict]:
        """Convert services to list of dictionaries"""
        return [
            {
                'id': s.id,
                'nom': s.nom,
                'places_disponibles': s.places_disponibles,
                'duree_stage_jours': s.duree_stage_jours
            } for s in services
        ]

    def _clear_existing_planning(self, promo_id: str):
        """Clear existing planning for the promotion"""
        # First delete rotations, then planning to avoid foreign key constraint violations
        from ..models import Rotation, StudentSchedule, StudentScheduleDetail

        # Get existing planning IDs for this promotion
        existing_plannings = self.db.query(Planning).filter(
            Planning.promo_id == promo_id).all()

        for planning in existing_plannings:
            # Delete in correct order to avoid foreign key violations:
            # 1. Delete student schedule details first
            # 2. Delete student schedules
            # 3. Delete rotations
            # 4. Delete planning

            # Get all student schedules for this planning
            student_schedules = self.db.query(StudentSchedule).filter(
                StudentSchedule.planning_id == planning.id).all()

            # Delete student schedule details first
            for schedule in student_schedules:
                self.db.query(StudentScheduleDetail).filter(
                    StudentScheduleDetail.schedule_id == schedule.id).delete()

            # Delete student schedules
            self.db.query(StudentSchedule).filter(
                StudentSchedule.planning_id == planning.id).delete()

            # Delete rotations
            self.db.query(Rotation).filter(
                Rotation.planning_id == planning.id).delete()

        # Now delete the planning
        self.db.query(Planning).filter(Planning.promo_id == promo_id).delete()

        # Commit the transaction
        self.db.commit()

    def _reset_algorithm_state(self, etudiants: List[Dict], date_debut_str: str):
        """Reset algorithm internal state"""
        self.service_occupation.clear()
        self.student_completed_services.clear()
        self.student_next_available_date.clear()

        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
        for etudiant in etudiants:
            self.student_completed_services[etudiant['id']] = set()
            self.student_next_available_date[etudiant['id']] = date_debut

    def _generate_optimized_planning(
        self, promotion: Dict, services: List[Dict], date_debut_str: str
    ) -> PlanningSchema:
        """
        Generate optimized planning with improved algorithm
        """
        etudiants = promotion['etudiants']
        nb_etudiants = len(etudiants)
        nb_services = len(services)

        # Validation
        self._validate_inputs(etudiants, services)

        # Sort services by name for consistent ordering
        services_sorted = sorted(services, key=lambda x: x['nom'])

        rotations = []
        max_iterations = nb_etudiants * nb_services * 2  # Increased safety margin
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Check if all students completed all services
            if self._all_students_completed(etudiants, nb_services):
                break

            progress_made = False

            # Process each student
            for etudiant in etudiants:
                if self._student_completed_all_services(etudiant['id'], nb_services):
                    continue

                # Find best service assignment
                best_assignment = self._find_best_service_assignment(
                    etudiant['id'], services_sorted
                )

                if best_assignment:
                    rotation = self._create_rotation(etudiant, best_assignment)
                    rotations.append(rotation)
                    self._update_algorithm_state(
                        etudiant['id'], best_assignment)
                    progress_made = True

            if not progress_made:
                # Advance all student dates by one day to break deadlock
                self._advance_all_student_dates()

        # Final validation
        self._validate_final_assignment(etudiants, nb_services)

        return PlanningSchema(
            id=str(uuid.uuid4()),
            promo_id=promotion['id'],
            promotion_year_id=None,
            annee_niveau=None,
            date_creation=datetime.now(),
            promo_nom=promotion['nom'],
            rotations=rotations
        )

    def _validate_inputs(self, etudiants: List[Dict], services: List[Dict]):
        """Validate input data"""
        if not services:
            raise HTTPException(
                status_code=400, detail="Aucun service disponible")

        if not etudiants:
            raise HTTPException(
                status_code=400, detail="Aucun étudiant dans la promotion")

        for service in services:
            if service['places_disponibles'] <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Service '{service['nom']}' n'a pas de places disponibles"
                )

    def _all_students_completed(self, etudiants: List[Dict], nb_services: int) -> bool:
        """Check if all students completed all services"""
        return all(
            len(self.student_completed_services[etudiant['id']]) == nb_services
            for etudiant in etudiants
        )

    def _student_completed_all_services(self, etudiant_id: str, nb_services: int) -> bool:
        """Check if a student completed all services"""
        return len(self.student_completed_services[etudiant_id]) == nb_services

    def _find_best_service_assignment(
        self, etudiant_id: str, services: List[Dict]
    ) -> Optional[Dict]:
        """Find the best service assignment for a student"""
        available_services = [
            s for s in services
            if s['id'] not in self.student_completed_services[etudiant_id]
        ]

        if not available_services:
            return None

        best_assignment = None
        best_score = -1

        for service in available_services:
            assignment = self._evaluate_service_assignment(
                service, self.student_next_available_date[etudiant_id]
            )

            if assignment and assignment['score'] > best_score:
                best_score = assignment['score']
                best_assignment = assignment

        return best_assignment

    def _evaluate_service_assignment(
        self, service: Dict, preferred_date: datetime
    ) -> Optional[Dict]:
        """Evaluate a service assignment and return best option"""
        service_id = service['id']
        duration = service['duree_stage_jours']
        capacity = service['places_disponibles']

        # Look for available slot within 90 days
        for day_offset in range(90):
            candidate_date = preferred_date + timedelta(days=day_offset)

            if self._is_service_available(service_id, candidate_date, duration, capacity):
                score = self._calculate_service_score(
                    service, candidate_date, day_offset)
                return {
                    'service': service,
                    'start_date': candidate_date,
                    'end_date': candidate_date + timedelta(days=duration - 1),
                    'score': score,
                    'order': 1  # Will be set properly by the caller
                }

        return None

    def _is_service_available(
        self, service_id: str, start_date: datetime, duration: int, capacity: int
    ) -> bool:
        """Check if service is available for the entire duration"""
        for day in range(duration):
            check_date = start_date + timedelta(days=day)
            date_str = check_date.strftime("%Y-%m-%d")

            if self.service_occupation[service_id][date_str] >= capacity:
                return False

        return True

    def _calculate_service_score(
        self, service: Dict, candidate_date: datetime, day_offset: int
    ) -> float:
        """Calculate score for service assignment"""
        service_id = service['id']
        capacity = service['places_disponibles']
        duration = service['duree_stage_jours']

        # 1. Availability score (higher for less occupied services)
        current_occupation = self.service_occupation[service_id][candidate_date.strftime(
            "%Y-%m-%d")]
        availability_score = (capacity - current_occupation) / capacity

        # 2. Capacity score (favor services with more total capacity)
        max_capacity = max(s['places_disponibles']
                           for s in self._get_all_services())
        capacity_score = capacity / max_capacity

        # 3. Urgency score (favor bottleneck services)
        urgency_score = (max_capacity - capacity + 1) / max_capacity

        # 4. Duration score (favor longer internships)
        max_duration = max(s['duree_stage_jours']
                           for s in self._get_all_services())
        duration_score = duration / max_duration

        # 5. Date penalty (prefer earlier dates)
        date_penalty = max(0, 1 - (day_offset / 30.0))

        # Weighted final score
        final_score = (
            availability_score * 0.35 +
            capacity_score * 0.20 +
            urgency_score * 0.20 +
            duration_score * 0.10 +
            date_penalty * 0.15
        )

        return final_score

    def _get_all_services(self) -> List[Dict]:
        """Get all services (cached for scoring)"""
        if not hasattr(self, '_cached_services'):
            self._cached_services = self._convert_services_to_list(
                self._get_services())
        return self._cached_services

    def _create_rotation(self, etudiant: Dict, assignment: Dict) -> RotationSchema:
        """Create rotation from assignment"""
        return RotationSchema(
            id=str(uuid.uuid4()),
            etudiant_id=etudiant['id'],
            service_id=assignment['service']['id'],
            date_debut=assignment['start_date'].strftime("%Y-%m-%d"),
            date_fin=assignment['end_date'].strftime("%Y-%m-%d"),
            ordre=assignment['order'],
            planning_id="",  # Will be set later
            etudiant_nom=f"{etudiant['prenom']} {etudiant['nom']}",
            service_nom=assignment['service']['nom']
        )

    def _update_algorithm_state(self, etudiant_id: str, assignment: Dict):
        """Update algorithm state after assignment"""
        service_id = assignment['service']['id']
        start_date = assignment['start_date']
        end_date = assignment['end_date']

        # Update service occupation
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            self.service_occupation[service_id][date_str] += 1
            current_date += timedelta(days=1)

        # Update student completed services
        self.student_completed_services[etudiant_id].add(service_id)

        # Update student next available date
        self.student_next_available_date[etudiant_id] = end_date + \
            timedelta(days=1)

    def _advance_all_student_dates(self):
        """Advance all student dates by one day to break deadlocks"""
        for etudiant_id in self.student_next_available_date:
            self.student_next_available_date[etudiant_id] += timedelta(days=1)

    def _validate_final_assignment(self, etudiants: List[Dict], nb_services: int):
        """Validate that all students have been assigned to all services"""
        for etudiant in etudiants:
            if len(self.student_completed_services[etudiant['id']]) != nb_services:
                raise HTTPException(
                    status_code=500,
                    detail=f"Impossible d'assigner tous les services à l'étudiant {etudiant['nom']}"
                )

    def _save_planning_to_db(self, planning_result: PlanningSchema) -> Planning:
        """Save planning result to database"""
        # Create the main planning record
        db_planning = Planning(
            id=planning_result.id,
            promo_id=planning_result.promo_id,
            promotion_year_id=planning_result.promotion_year_id,
            annee_niveau=planning_result.annee_niveau,
            date_creation=planning_result.date_creation
        )
        self.db.add(db_planning)
        self.db.flush()  # Get the ID

        # Create rotation records
        for rotation in planning_result.rotations:
            db_rotation = Rotation(
                id=rotation.id,
                etudiant_id=rotation.etudiant_id,
                service_id=rotation.service_id,
                date_debut=rotation.date_debut,
                date_fin=rotation.date_fin,
                ordre=rotation.ordre,
                planning_id=db_planning.id,
                promotion_year_id=db_planning.promotion_year_id  # <-- Ensure this is set
            )
            self.db.add(db_rotation)

        self.db.commit()
        self.db.refresh(db_planning)
        return db_planning

    def _create_student_schedules(self, db_planning: Planning, planning_result: PlanningSchema):
        """Create individual student schedules from the planning"""
        from .student_schedule import student_schedule

        # Group rotations by student
        rotations_by_student = defaultdict(list)
        for rotation in planning_result.rotations:
            rotations_by_student[rotation.etudiant_id].append(rotation)

        # Calculate overall planning dates
        all_start_dates = [datetime.strptime(
            r.date_debut, "%Y-%m-%d") for r in planning_result.rotations]
        all_end_dates = [datetime.strptime(
            r.date_fin, "%Y-%m-%d") for r in planning_result.rotations]

        planning_start_date = min(all_start_dates).strftime("%Y-%m-%d")
        planning_end_date = max(all_end_dates).strftime("%Y-%m-%d")

        # Create schedule for each student
        for etudiant_id, rotations in rotations_by_student.items():
            rotations_dict = [
                {
                    'id': rotation.id,
                    'service_id': rotation.service_id,
                    'service_nom': rotation.service_nom,
                    'ordre': rotation.ordre,
                    'date_debut': rotation.date_debut,
                    'date_fin': rotation.date_fin
                }
                for rotation in rotations
            ]

            student_schedule.create_from_planning(
                db=self.db,
                planning_id=db_planning.id,
                etudiant_id=etudiant_id,
                rotations=rotations_dict,
                date_debut_planning=planning_start_date,
                date_fin_planning=planning_end_date
            )

    def _analyze_planning_efficiency(
        self, planning: PlanningSchema, services: List[Dict]
    ) -> PlanningEfficiencyAnalysis:
        """Analyze the efficiency of the generated planning"""
        services_dict = {s['id']: s for s in services}

        # Calculate overall planning duration
        start_dates = [datetime.strptime(
            r.date_debut, "%Y-%m-%d") for r in planning.rotations]
        end_dates = [datetime.strptime(r.date_fin, "%Y-%m-%d")
                     for r in planning.rotations]

        planning_start = min(start_dates)
        planning_end = max(end_dates)
        total_duration = (planning_end - planning_start).days + 1

        # Calculate service occupation statistics
        service_occupation = {}
        for service in services:
            service_id = service['id']
            service_rotations = [
                r for r in planning.rotations if r.service_id == service_id]

            daily_occupation = defaultdict(int)
            for rotation in service_rotations:
                start_date = datetime.strptime(rotation.date_debut, "%Y-%m-%d")
                end_date = datetime.strptime(rotation.date_fin, "%Y-%m-%d")

                current_date = start_date
                while current_date <= end_date:
                    date_str = current_date.strftime("%Y-%m-%d")
                    daily_occupation[date_str] += 1
                    current_date += timedelta(days=1)

            if daily_occupation:
                avg_occupation = sum(
                    daily_occupation.values()) / len(daily_occupation)
                occupation_rate = avg_occupation / \
                    service['places_disponibles']
            else:
                avg_occupation = 0
                occupation_rate = 0

            service_occupation[service['nom']] = ServiceOccupationStats(
                taux_occupation=round(occupation_rate * 100, 1),
                jours_actifs=len(daily_occupation),
                occupation_moyenne=round(avg_occupation, 1)
            )

        return PlanningEfficiencyAnalysis(
            duree_totale_jours=total_duration,
            date_debut=planning_start.strftime("%Y-%m-%d"),
            date_fin=planning_end.strftime("%Y-%m-%d"),
            nb_rotations=len(planning.rotations),
            occupation_services=service_occupation
        )

    def _validate_planning(self, planning: PlanningSchema, services: List[Dict]) -> PlanningValidationResult:
        """Validate planning and return errors if any"""
        errors = []
        services_dict = {s['id']: s for s in services}

        # Check capacity constraints
        service_daily_occupation = defaultdict(lambda: defaultdict(list))

        for rotation in planning.rotations:
            service_id = rotation.service_id
            start_date = datetime.strptime(rotation.date_debut, "%Y-%m-%d")
            end_date = datetime.strptime(rotation.date_fin, "%Y-%m-%d")

            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                service_daily_occupation[service_id][date_str].append(
                    rotation.etudiant_nom)
                current_date += timedelta(days=1)

        # Check for capacity overruns
        for service_id, daily_occupation in service_daily_occupation.items():
            service = services_dict.get(service_id)
            if not service:
                continue

            capacity = service['places_disponibles']
            service_name = service['nom']

            for date_str, students in daily_occupation.items():
                if len(students) > capacity:
                    errors.append(
                        f"Dépassement de capacité dans '{service_name}' le {date_str}: "
                        f"{len(students)} étudiants pour {capacity} places disponibles"
                    )

        # Check that each student has all services
        student_services = defaultdict(set)
        for rotation in planning.rotations:
            student_services[rotation.etudiant_id].add(rotation.service_id)

        required_services = set(s['id'] for s in services)
        for student_id, assigned_services in student_services.items():
            if assigned_services != required_services:
                missing_services = required_services - assigned_services
                if missing_services:
                    missing_names = [services_dict[sid]['nom']
                                     for sid in missing_services]
                    # Find student name from rotations
                    student_name = next(
                        (r.etudiant_nom for r in planning.rotations if r.etudiant_id == student_id),
                        f"Student {student_id}"
                    )
                    errors.append(
                        f"Étudiant {student_name} n'a pas été assigné aux services: "
                        f"{', '.join(missing_names)}"
                    )

        return PlanningValidationResult(
            is_valid=len(errors) == 0,
            erreurs=errors
        )

    def _convert_to_planning_response(self, db_planning: Planning) -> PlanningSchema:
        """Convert database planning to response format"""
        rotations = []
        for rotation in db_planning.rotations:
            rotation_schema = RotationSchema(
                id=rotation.id,
                etudiant_id=rotation.etudiant_id,
                service_id=rotation.service_id,
                date_debut=rotation.date_debut,
                date_fin=rotation.date_fin,
                ordre=rotation.ordre,
                planning_id=rotation.planning_id,
                etudiant_nom=f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
                service_nom=rotation.service.nom
            )
            rotations.append(rotation_schema)

        return PlanningSchema(
            id=db_planning.id,
            promo_id=db_planning.promo_id,
            promotion_year_id=db_planning.promotion_year_id,
            annee_niveau=db_planning.annee_niveau,
            date_creation=db_planning.date_creation,
            promo_nom=db_planning.promotion.nom,
            rotations=rotations
        )


# Factory function
def get_advanced_planning_algorithm(db: Session) -> AdvancedPlanningAlgorithm:
    """Factory function to create AdvancedPlanningAlgorithm instance"""
    return AdvancedPlanningAlgorithm(db)
