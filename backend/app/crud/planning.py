from .planning_settings import planning_settings
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context
from ..schemas import PlanningCreate, PlanningBase
from ..models import Planning, Promotion, Service, Rotation, Etudiant, PromotionYear
from .base import CRUDBase
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid
from datetime import datetime, timedelta
import logging
import math

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CRUDPlanning(CRUDBase[Planning, PlanningCreate, PlanningBase]):
    def get_by_promotion(self, db: Session, *, promo_id: str) -> Optional[Planning]:
        """Get planning for a promotion"""
        return db.query(Planning).filter(Planning.promo_id == promo_id).first()

    def generate_planning(
        self, db: Session, *, promo_id: str, date_debut: str = None, all_years_mode: bool = False, promotion_year_id: str = None
    ) -> tuple[Planning, int, int]:
        """Generate optimized planning for a promotion using planning settings"""
        logger.debug(
            f"🚀 Starting planning generation for promotion: {promo_id}")
        logger.debug(f"📅 Date debut: {date_debut}")
        logger.debug(f"🟢 all_years_mode: {all_years_mode}")
        logger.debug(f"📅 promotion_year_id: {promotion_year_id}")

        # Get planning settings
        try:
            settings = planning_settings.get_or_create_default(db)
            logger.debug(f"✅ Planning settings loaded: {settings}")
        except Exception as e:
            logger.error(f"❌ Failed to load planning settings: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load planning settings: {str(e)}"
            )

        # Use settings start date if not provided
        if not date_debut:
            date_debut = settings.academic_year_start
            logger.debug(f"📅 Using settings start date: {date_debut}")

        try:
            promotion = db.query(Promotion).filter(
                Promotion.id == promo_id).first()
            if not promotion:
                logger.error(f"❌ Promotion not found: {promo_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Promotion non trouvée"
                )
            logger.debug(f"✅ Promotion found: {promotion.nom}")
        except Exception as e:
            logger.error(f"❌ Error loading promotion: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error loading promotion: {str(e)}"
            )

        # Get students (only active ones)
        try:
            etudiants = db.query(Etudiant).filter(
                Etudiant.promotion_id == promo_id,
                Etudiant.is_active == True
            ).all()
            if not etudiants:
                logger.error(f"❌ No active students in promotion: {promo_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Aucun étudiant actif dans cette promotion"
                )
            logger.debug(f"✅ Found {len(etudiants)} active students")
            for etudiant in etudiants:
                logger.debug(f"   - {etudiant.nom} {etudiant.prenom}")
        except Exception as e:
            logger.error(f"❌ Error loading students: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error loading students: {str(e)}"
            )

        if all_years_mode:
            # ALL YEARS MODE: Generate planning for all years of the speciality
            logger.debug(
                f"🔄 ALL YEARS MODE: Generating planning for all years")
            promotion_years = db.query(PromotionYear).filter(
                PromotionYear.promotion_id == promo_id
            ).order_by(PromotionYear.annee_niveau).all()
            if not promotion_years:
                logger.error(
                    f"❌ No promotion years found for promotion: {promo_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Aucune année de promotion trouvée"
                )
            logger.debug(f"✅ Found {len(promotion_years)} promotion years:")
            for year in promotion_years:
                logger.debug(
                    f"   - Year {year.annee_niveau}: {year.nom or 'Unnamed'}")
            created_plannings = []
            total_services = 0
            for promotion_year in promotion_years:
                year_services = promotion_year.services
                # Only students in this year
                year_students = [e for e in etudiants if getattr(
                    e, 'annee_courante', 1) == promotion_year.annee_niveau]
                if not year_services:
                    logger.warning(
                        f"⚠️ No services configured for year {promotion_year.annee_niveau}")
                    continue
                if not year_students:
                    logger.warning(
                        f"⚠️ No students found for year {promotion_year.annee_niveau}")
                    continue
                logger.debug(
                    f"✅ Found {len(year_services)} services and {len(year_students)} students for year {promotion_year.annee_niveau}")
                year_planning = self._generate_planning_for_year(
                    db, promotion, promotion_year, year_students, year_services,
                    settings, date_debut, logger
                )
                created_plannings.append(year_planning)
                total_services += len(year_services)
            # Return the first planning (or the active year planning if available)
            active_planning = next((p for p in created_plannings if p.promotion_year_id ==
                                    next((y.id for y in promotion_years if y.is_active), None)),
                                   created_plannings[0] if created_plannings else None)
            if not active_planning:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Aucun planning généré"
                )
            return created_plannings, total_services, len(etudiants)
        elif promotion_year_id:
            # SPECIFIC YEAR MODE: Generate planning for a specific year
            logger.debug(
                f"🔄 SPECIFIC YEAR MODE: Generating planning for year ID: {promotion_year_id}")
            specific_year = db.query(PromotionYear).filter(
                PromotionYear.id == promotion_year_id,
                PromotionYear.promotion_id == promo_id
            ).first()
            if not specific_year:
                logger.error(
                    f"❌ Specified year not found: {promotion_year_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Année spécifiée non trouvée"
                )
            logger.debug(
                f"✅ Specific year found: {specific_year.annee_niveau}")
            services = specific_year.services
            if not services:
                logger.error(
                    f"❌ No services configured for specified year: {specific_year.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Aucun service configuré pour cette année"
                )
            logger.debug(f"✅ Found {len(services)} services:")
            for service in services:
                logger.debug(
                    f"   - {service.nom} (duration: {service.duree_stage_jours} days, capacity: {service.places_disponibles})")
            planning = self._generate_planning_for_year(
                db, promotion, specific_year, etudiants, services,
                settings, date_debut, logger
            )
            return planning, len(services), len(etudiants)
        else:
            # ACTIVE YEAR ONLY MODE
            logger.debug(
                f"🔄 ACTIVE YEAR ONLY MODE: Generating planning for active year only")
            active_year = db.query(PromotionYear).filter(
                PromotionYear.promotion_id == promo_id,
                PromotionYear.is_active == True
            ).first()
            if not active_year:
                logger.error(
                    f"❌ No active year found for promotion: {promo_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Aucune année active trouvée pour cette promotion"
                )
            logger.debug(f"✅ Active year found: {active_year.annee_niveau}")
            services = active_year.services
            if not services:
                logger.error(
                    f"❌ No services configured for active year: {active_year.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Aucun service configuré pour cette année"
                )
            logger.debug(f"✅ Found {len(services)} services:")
            for service in services:
                logger.debug(
                    f"   - {service.nom} (duration: {service.duree_stage_jours} days, capacity: {service.places_disponibles})")
            planning = self._generate_planning_for_year(
                db, promotion, active_year, etudiants, services,
                settings, date_debut, logger
            )
            return planning, len(services), len(etudiants)

    def generate_planning_for_all_years(
        self, db: Session, *, promo_id: str, date_debut: str, promotion_years: List
    ) -> tuple[Planning, int, int]:
        """Generate one big planning that combines all years into a single comprehensive plan"""
        logger.debug(
            f"🚀 Starting ALL YEARS planning generation for promotion: {promo_id}")
        logger.debug(f"📅 Date debut: {date_debut}")
        logger.debug(f"📅 Number of years to combine: {len(promotion_years)}")

        # Get planning settings
        try:
            from .planning_settings import planning_settings
            settings = planning_settings.get_or_create_default(db)
            logger.debug(f"✅ Planning settings loaded: {settings}")
        except Exception as e:
            logger.error(f"❌ Error loading planning settings: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error loading planning settings: {str(e)}"
            )

        # Get promotion
        promotion = db.query(Promotion).filter(
            Promotion.id == promo_id).first()
        if not promotion:
            logger.error(f"❌ Promotion not found: {promo_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion non trouvée"
            )
        logger.debug(f"✅ Promotion found: {promotion.nom}")

        # Get all active students
        etudiants = db.query(Etudiant).filter(
            Etudiant.promotion_id == promo_id,
            Etudiant.is_active == True
        ).all()
        if not etudiants:
            logger.error(
                f"❌ No active students found for promotion: {promo_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun étudiant actif trouvé pour cette promotion"
            )
        logger.debug(f"✅ Found {len(etudiants)} active students")
        for etudiant in etudiants:
            logger.debug(f"   - {etudiant.prenom} {etudiant.nom}")

        # Collect all services from all years
        all_services = []
        all_services_by_year = {}

        for promotion_year in promotion_years:
            year_services = promotion_year.services
            if year_services:
                all_services.extend(year_services)
                all_services_by_year[promotion_year.id] = year_services
                logger.debug(
                    f"✅ Found {len(year_services)} services for {promotion_year.nom}:")
                for service in year_services:
                    logger.debug(
                        f"   - {service.nom} (duration: {service.duree_stage_jours} days, capacity: {service.places_disponibles})")
            else:
                logger.warning(
                    f"⚠️ No services configured for {promotion_year.nom}")

        if not all_services:
            logger.error(f"❌ No services found across all years")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun service configuré pour les années sélectionnées"
            )

        logger.debug(f"📊 Total services across all years: {len(all_services)}")

        # Generate the big planning
        planning = self._generate_big_planning_for_all_years(
            db, promotion, promotion_years, etudiants, all_services, all_services_by_year,
            settings, date_debut, logger
        )

        return planning, len(all_services), len(etudiants)

    def _generate_planning_for_year(self, db, promotion, promotion_year, etudiants, services, settings, date_debut, logger):
        """Helper to generate a single planning for a specific promotion year."""
        logger.debug(
            f"🔧 _generate_planning_for_year called with date_debut: {date_debut}")
        logger.debug(
            f"🔧 Promotion year: {promotion_year.nom} (ID: {promotion_year.id})")
        logger.debug(f"🔧 Calendar year: {promotion_year.annee_calendaire}")

        # Clear existing planning properly
        existing_planning = self.get_by_promotion(db, promo_id=promotion.id)
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
            promo_id=promotion.id,
            promotion_year_id=promotion_year.id,
            annee_niveau=promotion_year.annee_niveau
        )
        db.add(db_planning)
        db.flush()

        # Calculate planning constraints
        try:
            nb_etudiants = len(etudiants)
            nb_services = len(services)
            date_debut_dt = datetime.strptime(date_debut, "%Y-%m-%d")

            # For mandatory completion, we extend the time limit as needed
            # Initial estimate: give enough time for all students to complete all services
            estimated_total_days = 0
            for service in services:
                # Each service needs to run enough times to accommodate all students
                # Taking into account service capacity and duration
                service_capacity = min(
                    service.places_disponibles, settings.max_concurrent_students)
                service_runs_needed = math.ceil(
                    nb_etudiants / service_capacity)
                estimated_total_days = max(
                    estimated_total_days, service_runs_needed * service.duree_stage_jours)

            # Add buffer for breaks and scheduling flexibility
            buffer_days = estimated_total_days * 0.3  # 30% buffer
            total_duration_days = estimated_total_days + buffer_days
            date_fin_limite = date_debut_dt + \
                timedelta(days=total_duration_days)

            logger.debug(f"📊 Planning constraints:")
            logger.debug(f"   - Students: {nb_etudiants}")
            logger.debug(f"   - Services: {nb_services}")
            logger.debug(f"   - Start date: {date_debut_dt}")
            logger.debug(f"   - Estimated end date: {date_fin_limite}")
            logger.debug(f"   - Total duration: {total_duration_days} days")
            logger.debug(
                f"   - MANDATORY COMPLETION: ALL students must complete ALL services")
        except Exception as e:
            logger.error(f"❌ Error calculating planning constraints: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error calculating planning constraints: {str(e)}"
            )

        # For mandatory completion, we use ALL services - no selection/filtering
        try:
            logger.debug(f"✅ Using ALL services for mandatory completion:")
            for service in services:
                logger.debug(
                    f"   - {service.nom} (duration: {service.duree_stage_jours} days, capacity: {service.places_disponibles})")

            nb_services = len(services)
            if nb_services == 0:
                logger.error("❌ No services available")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Aucun service disponible"
                )

            logger.debug(f"📊 Mandatory completion requirements:")
            logger.debug(
                f"   - Each student must complete: {nb_services} services")
            logger.debug(
                f"   - Total rotations needed: {nb_etudiants * nb_services}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error in service preparation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error in service preparation: {str(e)}"
            )

        # Initialize tracking variables
        rotations = []
        service_occupation = {}
        student_completed_services = {}
        student_next_available_date = {}
        student_waiting_queue = {}  # Track students waiting for specific services
        assignment_history = []  # Track assignments for backtracking

        for etudiant in etudiants:
            student_completed_services[etudiant.id] = set()
            student_next_available_date[etudiant.id] = date_debut_dt
            # List of service IDs student is waiting for
            student_waiting_queue[etudiant.id] = []

        # Mandatory completion algorithm - continues until ALL students complete ALL services
        max_iterations = nb_etudiants * nb_services * 3  # More generous iteration limit
        iteration = 0
        stagnation_count = 0
        completion_target = nb_etudiants * nb_services  # Total rotations needed

        logger.debug(f"🔄 Starting MANDATORY COMPLETION algorithm:")
        logger.debug(f"   - Max iterations: {max_iterations}")
        logger.debug(f"   - Completion target: {completion_target} rotations")
        logger.debug(
            f"   - Extension allowed: planning can extend beyond original duration")

        logger.debug(f"📋 Planning settings:")
        logger.debug(
            f"   - Max concurrent students (global): {settings.max_concurrent_students}")
        logger.debug(f"📋 Service capacities:")
        for service in services:
            effective_capacity = min(
                service.places_disponibles, settings.max_concurrent_students)
            logger.debug(
                f"   - {service.nom}: {service.places_disponibles} → effective: {effective_capacity}")

        while iteration < max_iterations:
            iteration += 1
            progress_made = False

            # Check completion status
            current_rotations = len(rotations)
            completion_rate = (current_rotations / completion_target) * \
                100 if completion_target > 0 else 0

            if iteration % 10 == 0:
                logger.debug(f"🔄 Iteration {iteration}/{max_iterations}")
                logger.debug(
                    f"   - Rotations created: {current_rotations}/{completion_target} ({completion_rate:.1f}%)")

                # Show student completion status
                incomplete_students = 0
                for etudiant in etudiants:
                    completed_count = len(
                        student_completed_services[etudiant.id])
                    if completed_count < nb_services:
                        incomplete_students += 1

                logger.debug(
                    f"   - Students with incomplete schedules: {incomplete_students}/{nb_etudiants}")

            # Check if we've achieved mandatory completion
            if current_rotations >= completion_target:
                # Verify all students have completed all services
                all_complete = True
                for etudiant in etudiants:
                    if len(student_completed_services[etudiant.id]) < nb_services:
                        all_complete = False
                        missing_services = nb_services - \
                            len(student_completed_services[etudiant.id])
                        logger.debug(
                            f"   - {etudiant.nom} still needs {missing_services} services")

                if all_complete:
                    logger.debug("🎉 MANDATORY COMPLETION ACHIEVED!")
                    logger.debug(
                        f"   - All {nb_etudiants} students completed all {nb_services} services")
                    logger.debug(f"   - Total rotations: {current_rotations}")
                    break

            # Sort students by completion priority (least completed first, then by next available date)
            etudiants_sorted = sorted(etudiants, key=lambda e: (
                # Primary: number of completed services (ascending - help students with fewer services first)
                len(student_completed_services[e.id]),
                # Secondary: next available date (ascending - help students who can start sooner)
                student_next_available_date[e.id]
            ))

            for etudiant in etudiants_sorted:
                # Check if student has completed all services
                if len(student_completed_services[etudiant.id]) >= nb_services:
                    continue

                # For mandatory completion, students can be scheduled far in the future if needed
                current_date = student_next_available_date[etudiant.id]

                # Find services this student hasn't completed yet
                remaining_services = [
                    s for s in services if s.id not in student_completed_services[etudiant.id]]

                if not remaining_services:
                    continue

                # Find best available service from remaining services
                service_options = []
                best_assignment = None

                for service in remaining_services:
                    # Find earliest available slot for this service
                    earliest_start = current_date
                    service_found = False

                    # Look for available slot within reasonable future (up to 1 year ahead)
                    max_search_date = current_date + timedelta(days=365)
                    search_date = earliest_start

                    while search_date <= max_search_date:
                        service_end_date = search_date + \
                            timedelta(days=service.duree_stage_jours - 1)

                        # Check service availability for entire duration
                        service_id = service.id
                        if service_id not in service_occupation:
                            service_occupation[service_id] = {}

                        max_concurrent = min(
                            service.places_disponibles, settings.max_concurrent_students)

                        # Check availability for entire service duration
                        available_for_duration = True
                        check_date = search_date
                        while check_date <= service_end_date:
                            date_str = check_date.strftime("%Y-%m-%d")
                            if date_str not in service_occupation[service_id]:
                                service_occupation[service_id][date_str] = 0

                            if service_occupation[service_id][date_str] >= max_concurrent:
                                available_for_duration = False
                                break
                            check_date += timedelta(days=1)

                        if available_for_duration:
                            # Calculate priority score for this service option
                            # Priority factors: service availability, student workload balance, service demand

                            # Service availability score
                            total_availability = 0
                            days_count = 0
                            check_date = search_date
                            while check_date <= service_end_date:
                                date_str = check_date.strftime("%Y-%m-%d")
                                current_occupation = service_occupation[service_id].get(
                                    date_str, 0)
                                total_availability += (max_concurrent -
                                                       current_occupation)
                                days_count += 1
                                check_date += timedelta(days=1)
                            availability_score = (
                                total_availability / days_count) / max_concurrent

                            # Student urgency score (students with fewer completed services get priority)
                            student_completion_count = len(
                                student_completed_services[etudiant.id])
                            urgency_score = (
                                nb_services - student_completion_count) / nb_services

                            # Service demand score (prefer services with fewer total assignments)
                            service_total_assignments = sum(
                                1 for s in student_completed_services.values() if service.id in s)
                            target_assignments = nb_etudiants
                            if service_total_assignments < target_assignments:
                                demand_score = (
                                    target_assignments - service_total_assignments) / target_assignments
                            else:
                                demand_score = 0.1  # Small score for overloaded services

                            # Time delay penalty (prefer earlier start dates)
                            days_delay = (search_date - current_date).days
                            # Reduce score for delays > 30 days
                            delay_penalty = max(0, 1 - (days_delay / 30))

                            # Combined score
                            score = (availability_score * 0.3 +
                                     urgency_score * 0.4 +
                                     demand_score * 0.2 +
                                     delay_penalty * 0.1)

                            service_options.append({
                                'service': service,
                                'start_date': search_date,
                                'end_date': service_end_date,
                                'order': len(rotations) + 1,
                                'score': score,
                                'days_delay': days_delay
                            })

                            service_found = True
                            break  # Found earliest available slot for this service

                        # Try next day
                        search_date += timedelta(days=1)

                    if not service_found:
                        logger.warning(
                            f"⚠️  No available slot found for {etudiant.nom} in {service.nom} within search window")

                # Select best option from available services
                if service_options:
                    # Sort by score (prioritize high-priority assignments)
                    service_options.sort(
                        key=lambda x: x['score'], reverse=True)
                    best_assignment = service_options[0]

                    # Log if assignment is delayed
                    if best_assignment['days_delay'] > 0:
                        logger.debug(
                            f"🕐 {etudiant.nom} assigned to {best_assignment['service'].nom} with {best_assignment['days_delay']} day delay")

                # Create rotation if assignment found
                if best_assignment:
                    # Double-check capacity before finalizing assignment
                    service_id = best_assignment['service'].id
                    start_date = best_assignment['start_date']
                    end_date = best_assignment['end_date']
                    max_allowed = min(
                        best_assignment['service'].places_disponibles, settings.max_concurrent_students)

                    # Verify no capacity violation will occur
                    capacity_violation = False
                    check_date = start_date
                    while check_date <= end_date:
                        date_str = check_date.strftime("%Y-%m-%d")
                        current_occupancy = service_occupation.get(
                            service_id, {}).get(date_str, 0)
                        if current_occupancy >= max_allowed:
                            capacity_violation = True
                            logger.warning(
                                f"⚠️  Capacity violation prevented for {best_assignment['service'].nom} on {date_str}: {current_occupancy}/{max_allowed}")
                            break
                        check_date += timedelta(days=1)

                    if capacity_violation:
                        # Skip this assignment to prevent violation
                        continue

                    rotation = Rotation(
                        id=str(uuid.uuid4()),
                        etudiant_id=etudiant.id,
                        service_id=best_assignment['service'].id,
                        date_debut=best_assignment['start_date'].strftime(
                            "%Y-%m-%d"),
                        date_fin=best_assignment['end_date'].strftime(
                            "%Y-%m-%d"),
                        ordre=best_assignment['order'],
                        planning_id=db_planning.id,
                        promotion_year_id=promotion_year.id  # NEW: set the year
                    )
                    rotations.append(rotation)
                    db.add(rotation)

                    # Track assignment for backtracking
                    assignment_history.append({
                        'rotation': rotation,
                        'etudiant_id': etudiant.id,
                        'service_id': best_assignment['service'].id,
                        'start_date': best_assignment['start_date'],
                        'end_date': best_assignment['end_date'],
                        'iteration': iteration
                    })

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

                    # Log successful assignment
                    if iteration % 25 == 0:
                        completed_services = len(
                            student_completed_services[etudiant.id])
                        logger.debug(
                            f"✅ {etudiant.nom} → {best_assignment['service'].nom} ({completed_services}/{nb_services} services)")

                    progress_made = True

            # Handle stagnation with more aggressive backtracking for mandatory completion
            if not progress_made:
                stagnation_count += 1

                # If stagnated, try backtracking more aggressively
                if stagnation_count >= 2 and len(assignment_history) > 0:
                    # For mandatory completion, we're more aggressive with backtracking
                    # Remove up to 33% of assignments
                    backtrack_count = min(10, len(assignment_history) // 3)

                    logger.debug(
                        f"🔄 Backtracking {backtrack_count} assignments due to stagnation")

                    for _ in range(backtrack_count):
                        if not assignment_history:
                            break

                        # Remove last assignment
                        last_assignment = assignment_history.pop()

                        # Remove from database
                        db.delete(last_assignment['rotation'])
                        rotations.remove(last_assignment['rotation'])

                        # Update tracking
                        student_completed_services[last_assignment['etudiant_id']].discard(
                            last_assignment['service_id'])

                        # Recalculate student next available date
                        student_rotations = [
                            r for r in rotations if r.etudiant_id == last_assignment['etudiant_id']]
                        if student_rotations:
                            latest_rotation = max(
                                student_rotations, key=lambda r: datetime.strptime(r.date_fin, "%Y-%m-%d"))
                            student_next_available_date[last_assignment['etudiant_id']] = datetime.strptime(
                                latest_rotation.date_fin, "%Y-%m-%d") + timedelta(days=settings.break_days_between_rotations)
                        else:
                            student_next_available_date[last_assignment['etudiant_id']
                                                        ] = date_debut_dt

                        # Update service occupation
                        current_date = last_assignment['start_date']
                        while current_date <= last_assignment['end_date']:
                            date_str = current_date.strftime("%Y-%m-%d")
                            if (last_assignment['service_id'] in service_occupation and
                                    date_str in service_occupation[last_assignment['service_id']]):
                                service_occupation[last_assignment['service_id']
                                                   ][date_str] -= 1
                                if service_occupation[last_assignment['service_id']][date_str] <= 0:
                                    del service_occupation[last_assignment['service_id']][date_str]
                            current_date += timedelta(days=1)

                    stagnation_count = 0
                    continue

                # If we've stagnated for too long, extend time limits
                elif stagnation_count >= 5:
                    logger.debug(
                        "🕐 Extending time limits due to persistent stagnation")
                    # Extend the search window for finding available slots
                    # This is handled in the service assignment loop above
                    stagnation_count = 0
                    continue

            else:
                stagnation_count = 0

        # Final completion check
        final_completion_check = True
        incomplete_students = []

        for etudiant in etudiants:
            completed_services = len(student_completed_services[etudiant.id])
            if completed_services < nb_services:
                final_completion_check = False
                missing_count = nb_services - completed_services
                incomplete_students.append(
                    f"{etudiant.nom} (missing {missing_count} services)")

        if not final_completion_check:
            logger.warning(f"⚠️  MANDATORY COMPLETION NOT ACHIEVED:")
            logger.warning(
                f"   - Incomplete students: {len(incomplete_students)}")
            for student_info in incomplete_students:
                logger.warning(f"   - {student_info}")
            logger.warning(
                f"   - Algorithm stopped after {iteration} iterations")
            logger.warning(
                f"   - This may require manual intervention or longer time limits")
        else:
            logger.info(f"🎉 MANDATORY COMPLETION SUCCESSFUL!")
            logger.info(
                f"   - All {nb_etudiants} students completed all {nb_services} services")
            logger.info(f"   - Total rotations: {len(rotations)}")
            logger.info(f"   - Completed in {iteration} iterations")

        # Continue with validation...

        # Validate planning quality before committing
        try:
            logger.debug(
                f"🔍 Validating planning quality with {len(rotations)} rotations")
            validation_results = self._validate_planning_quality(
                db_planning, rotations, etudiants, services, settings)

            logger.debug(f"✅ Validation complete:")
            logger.debug(
                f"   - Critical errors: {len(validation_results['critical_errors'])}")
            logger.debug(
                f"   - Warnings: {len(validation_results['warnings'])}")
            logger.debug(
                f"   - Quality score: {validation_results['quality_score']:.2f}")

            if validation_results['critical_errors']:
                for error in validation_results['critical_errors']:
                    logger.error(f"   ❌ {error}")

            if validation_results['warnings']:
                for warning in validation_results['warnings']:
                    logger.warning(f"   ⚠️  {warning}")

            # If validation fails critically, raise error
            if validation_results['critical_errors']:
                logger.error(
                    "❌ Planning validation failed with critical errors")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Planning quality validation failed: {'; '.join(validation_results['critical_errors'])}"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error during validation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during validation: {str(e)}"
            )

        # Commit the planning
        try:
            logger.debug("💾 Committing planning to database")
            db.commit()
            db.refresh(db_planning)
            logger.debug(
                f"✅ Planning successfully created with ID: {db_planning.id}")
            return db_planning
        except Exception as e:
            logger.error(f"❌ Error committing planning: {e}")
            db.rollback()
            handle_unique_constraint(e, "Le planning")

    def _generate_big_planning_for_all_years(
        self, db, promotion, promotion_years, etudiants, all_services, all_services_by_year,
        settings, date_debut, logger
    ):
        """Helper to generate one big planning that combines all years in sequence"""
        logger.debug(
            f"🔧 _generate_big_planning_for_all_years called with date_debut: {date_debut}")

        # Clear existing planning properly
        existing_planning = self.get_by_promotion(db, promo_id=promotion.id)
        if existing_planning:
            # Delete in correct order to avoid foreign key violations
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
            db.flush()

        # Create new big planning (no specific year since it's combined)
        db_planning = Planning(
            id=str(uuid.uuid4()),
            promo_id=promotion.id,
            promotion_year_id=None,  # No specific year for combined planning
            annee_niveau=None  # No specific level for combined planning
        )
        db.add(db_planning)
        db.flush()

        # Sort promotion years by annee_niveau to ensure proper sequence
        promotion_years_sorted = sorted(
            promotion_years, key=lambda x: x.annee_niveau)
        logger.debug(f"📅 Years sorted by academic level:")
        for year in promotion_years_sorted:
            logger.debug(
                f"   - {year.nom} (Level: {year.annee_niveau}, Calendar: {year.annee_calendaire})")

        # Generate rotations for each year in sequence
        all_rotations = []
        current_date = None

        for i, promotion_year in enumerate(promotion_years_sorted):
            # Determine start date for this year
            if i == 0:
                # First year: use the provided date_debut or construct from calendar year
                if promotion_year.date_debut:
                    year_start_date = datetime.strptime(
                        promotion_year.date_debut, "%Y-%m-%d")
                else:
                    year_start_date = datetime.strptime(
                        f"{promotion_year.annee_calendaire}-01-01", "%Y-%m-%d")
            else:
                # Subsequent years: start from the next academic year
                year_start_date = datetime.strptime(
                    f"{promotion_year.annee_calendaire}-01-01", "%Y-%m-%d")

            logger.debug(
                f"📅 Generating planning for {promotion_year.nom} starting: {year_start_date.strftime('%Y-%m-%d')}")

            # Get services for this year
            year_services = all_services_by_year.get(promotion_year.id, [])
            if not year_services:
                logger.warning(
                    f"⚠️ No services configured for {promotion_year.nom}, skipping")
                continue

            logger.debug(
                f"✅ Found {len(year_services)} services for {promotion_year.nom}:")
            for service in year_services:
                logger.debug(
                    f"   - {service.nom} (duration: {service.duree_stage_jours} days, capacity: {service.places_disponibles})")

            # Generate rotations for this year
            year_rotations = self._generate_rotations_for_year(
                etudiants, year_services, settings, year_start_date, logger
            )

            # Add year information to rotations and add to big planning
            for j, (etudiant, service, start_date, end_date) in enumerate(year_rotations):
                rotation = Rotation(
                    id=str(uuid.uuid4()),
                    etudiant_id=etudiant.id,
                    service_id=service.id,
                    date_debut=start_date.strftime("%Y-%m-%d"),
                    date_fin=end_date.strftime("%Y-%m-%d"),
                    # Global order across all years
                    ordre=len(all_rotations) + j + 1,
                    planning_id=db_planning.id,
                    promotion_year_id=promotion_year.id  # Assign to the appropriate year
                )
                db.add(rotation)
                all_rotations.append(rotation)

            logger.info(
                f"✅ Completed planning for {promotion_year.nom}: {len(year_rotations)} rotations")

        if not all_rotations:
            logger.error("❌ No rotations generated for any year")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucune rotation générée pour les années sélectionnées"
            )

        db.commit()
        logger.info(f"🎉 BIG PLANNING WITH CHAINED YEARS SUCCESSFUL!")
        logger.info(
            f"   - Total rotations across all years: {len(all_rotations)}")
        logger.info(f"   - Years processed: {len(promotion_years_sorted)}")

        # Validate the big planning quality
        self._validate_planning_quality(
            db_planning, all_rotations, etudiants, all_services, settings)

        return db_planning

    def _generate_rotations_for_year(
        self, etudiants, services, settings, year_start_date, logger
    ):
        """Generate rotations for a specific year starting from the given date"""
        logger.debug(
            f"🔄 Generating rotations for year starting: {year_start_date.strftime('%Y-%m-%d')}")

        nb_etudiants = len(etudiants)
        nb_services = len(services)

        # Calculate planning constraints for this year
        estimated_total_days = 0
        for service in services:
            service_capacity = min(
                service.places_disponibles, settings.max_concurrent_students)
            service_runs_needed = math.ceil(nb_etudiants / service_capacity)
            estimated_total_days = max(
                estimated_total_days, service_runs_needed * service.duree_stage_jours)

        # Add buffer for breaks and scheduling flexibility
        buffer_days = estimated_total_days * 0.3  # 30% buffer
        total_duration_days = estimated_total_days + buffer_days
        year_end_date = year_start_date + timedelta(days=total_duration_days)

        logger.debug(f"📊 Year planning constraints:")
        logger.debug(f"   - Students: {nb_etudiants}")
        logger.debug(f"   - Services: {nb_services}")
        logger.debug(f"   - Start date: {year_start_date}")
        logger.debug(f"   - Estimated end date: {year_end_date}")
        logger.debug(f"   - Total duration: {total_duration_days} days")

        # Use the existing mandatory completion algorithm from _generate_planning_for_year
        # Initialize tracking variables
        rotations = []
        service_occupation = {}  # Track service capacity per date
        student_completed_services = {}  # Track which services each student has completed
        student_next_available_date = {}  # Track when each student is available next

        # Initialize student tracking
        for etudiant in etudiants:
            student_completed_services[etudiant.id] = set()
            student_next_available_date[etudiant.id] = year_start_date
            student_waiting_queue = {}  # Not used in this simplified version

        # Mandatory completion algorithm - continues until ALL students complete ALL services
        max_iterations = nb_etudiants * nb_services * 3  # More generous iteration limit
        iteration = 0
        completion_target = nb_etudiants * nb_services  # Total rotations needed

        logger.debug(f"🔄 Starting MANDATORY COMPLETION algorithm:")
        logger.debug(f"   - Max iterations: {max_iterations}")
        logger.debug(f"   - Completion target: {completion_target} rotations")
        logger.debug(
            f"   - Extension allowed: planning can extend beyond original duration")

        while iteration < max_iterations:
            iteration += 1
            progress_made = False

            # Check completion status
            current_rotations = len(rotations)
            completion_rate = (current_rotations / completion_target) * \
                100 if completion_target > 0 else 0

            if iteration % 10 == 0:
                logger.debug(f"🔄 Iteration {iteration}/{max_iterations}")
                logger.debug(
                    f"   - Rotations created: {current_rotations}/{completion_target} ({completion_rate:.1f}%)")

            # Check if we've achieved mandatory completion
            if current_rotations >= completion_target:
                # Verify all students have completed all services
                all_complete = True
                for etudiant in etudiants:
                    if len(student_completed_services[etudiant.id]) < nb_services:
                        all_complete = False
                        missing_services = nb_services - \
                            len(student_completed_services[etudiant.id])
                        logger.debug(
                            f"   - {etudiant.nom} still needs {missing_services} services")

                if all_complete:
                    logger.debug("🎉 MANDATORY COMPLETION ACHIEVED!")
                    logger.debug(
                        f"   - All {nb_etudiants} students completed all {nb_services} services")
                    logger.debug(f"   - Total rotations: {current_rotations}")
                    break

            # Sort students by completion priority (least completed first, then by next available date)
            etudiants_sorted = sorted(etudiants, key=lambda e: (
                # Primary: number of completed services
                len(student_completed_services[e.id]),
                # Secondary: next available date
                student_next_available_date[e.id]
            ))

            for etudiant in etudiants_sorted:
                # Check if student has completed all services
                if len(student_completed_services[etudiant.id]) >= nb_services:
                    continue

                current_date = student_next_available_date[etudiant.id]

                # Find services this student hasn't completed yet
                remaining_services = [
                    s for s in services if s.id not in student_completed_services[etudiant.id]]

                if not remaining_services:
                    continue

                # Find best available service from remaining services
                service_options = []

                for service in remaining_services:
                    # Find earliest available slot for this service
                    earliest_start = current_date
                    service_found = False

                    # Look for available slot within reasonable future (up to 1 year ahead)
                    max_search_date = current_date + timedelta(days=365)
                    search_date = earliest_start

                    while search_date <= max_search_date:
                        service_end_date = search_date + \
                            timedelta(days=service.duree_stage_jours - 1)

                        # Check service availability for entire duration
                        service_id = service.id
                        if service_id not in service_occupation:
                            service_occupation[service_id] = {}

                        max_concurrent = min(
                            service.places_disponibles, settings.max_concurrent_students)

                        # Check availability for entire service duration
                        available_for_duration = True
                        check_date = search_date
                        while check_date <= service_end_date:
                            date_str = check_date.strftime("%Y-%m-%d")
                            if date_str not in service_occupation[service_id]:
                                service_occupation[service_id][date_str] = 0

                            if service_occupation[service_id][date_str] >= max_concurrent:
                                available_for_duration = False
                                break
                            check_date += timedelta(days=1)

                        if available_for_duration:
                            # Calculate priority score
                            # Service availability score
                            total_availability = 0
                            days_count = 0
                            check_date = search_date
                            while check_date <= service_end_date:
                                date_str = check_date.strftime("%Y-%m-%d")
                                current_occupation = service_occupation[service_id].get(
                                    date_str, 0)
                                total_availability += (max_concurrent -
                                                       current_occupation)
                                days_count += 1
                                check_date += timedelta(days=1)
                            availability_score = (
                                total_availability / days_count) / max_concurrent

                            # Student urgency score
                            student_completion_count = len(
                                student_completed_services[etudiant.id])
                            urgency_score = (
                                nb_services - student_completion_count) / nb_services

                            # Service demand score
                            service_total_assignments = sum(
                                1 for s in student_completed_services.values() if service.id in s)
                            target_assignments = nb_etudiants
                            if service_total_assignments < target_assignments:
                                demand_score = (
                                    target_assignments - service_total_assignments) / target_assignments
                            else:
                                demand_score = 0.1

                            # Time delay penalty
                            days_delay = (search_date - current_date).days
                            delay_penalty = max(0, 1 - (days_delay / 30))

                            # Combined score
                            score = (availability_score * 0.3 + urgency_score *
                                     0.4 + demand_score * 0.2 + delay_penalty * 0.1)

                            service_options.append({
                                'service': service,
                                'start_date': search_date,
                                'end_date': service_end_date,
                                'order': len(rotations) + 1,
                                'score': score,
                                'days_delay': days_delay
                            })

                            service_found = True
                            break

                        # Try next day
                        search_date += timedelta(days=1)

                # Select best option from available services
                if service_options:
                    # Sort by score (highest first)
                    service_options.sort(
                        key=lambda x: x['score'], reverse=True)
                    best_option = service_options[0]

                    service = best_option['service']
                    start_date = best_option['start_date']
                    end_date = best_option['end_date']

                    # Create rotation
                    rotation_data = (etudiant, service, start_date, end_date)
                    rotations.append(rotation_data)

                    # Update tracking
                    student_completed_services[etudiant.id].add(service.id)
                    student_next_available_date[etudiant.id] = end_date + \
                        timedelta(days=settings.break_days_between_rotations)

                    # Update service occupation
                    service_id = service.id
                    check_date = start_date
                    while check_date <= end_date:
                        date_str = check_date.strftime("%Y-%m-%d")
                        if date_str not in service_occupation[service_id]:
                            service_occupation[service_id][date_str] = 0
                        service_occupation[service_id][date_str] += 1
                        check_date += timedelta(days=1)

                    progress_made = True
                    logger.debug(
                        f"🕐 {etudiant.nom} assigned to {service.nom} with {best_option['days_delay']} day delay")
                else:
                    logger.warning(
                        f"⚠️  No available slot found for {etudiant.nom} in any remaining service")

            if not progress_made:
                logger.warning(
                    f"⚠️  No progress made in iteration {iteration}")
                break

        # Final completion check
        current_rotations = len(rotations)
        if current_rotations >= completion_target:
            all_complete = True
            for etudiant in etudiants:
                if len(student_completed_services[etudiant.id]) < nb_services:
                    all_complete = False
                    break

            if all_complete:
                logger.info(f"🎉 MANDATORY COMPLETION SUCCESSFUL!")
                logger.info(
                    f"   - All {nb_etudiants} students completed all {nb_services} services")
                logger.info(f"   - Total rotations: {current_rotations}")
                logger.info(f"   - Completed in {iteration} iterations")
            else:
                logger.warning(f"⚠️  MANDATORY COMPLETION NOT ACHIEVED:")
                logger.warning(
                    f"   - Created {current_rotations} rotations out of {completion_target} needed")
                for etudiant in etudiants:
                    completed_count = len(
                        student_completed_services[etudiant.id])
                    logger.warning(
                        f"   - {etudiant.nom}: {completed_count}/{nb_services} services completed")
        else:
            logger.warning(f"⚠️  MANDATORY COMPLETION NOT ACHIEVED:")
            logger.warning(
                f"   - Created {current_rotations} rotations out of {completion_target} needed")

        logger.debug(f"✅ Generated {len(rotations)} rotations for this year")
        return rotations

    def _validate_planning_quality(self, planning, rotations, etudiants, services, settings):
        """Validate planning quality and return detailed metrics"""
        logger.debug("🔍 Starting planning quality validation")
        validation_results = {
            'critical_errors': [],
            'warnings': [],
            'metrics': {},
            'quality_score': 0.0
        }

        # 1. Constraint validation
        service_concurrent_capacity = {}  # Track concurrent capacity by date
        student_assignments = {}

        for rotation in rotations:
            # Track student assignments
            if rotation.etudiant_id not in student_assignments:
                student_assignments[rotation.etudiant_id] = []
            student_assignments[rotation.etudiant_id].append(rotation)

            # Track concurrent capacity for each service by date
            if rotation.service_id not in service_concurrent_capacity:
                service_concurrent_capacity[rotation.service_id] = {}

            # Calculate concurrent occupancy for each day of the rotation
            start_date = datetime.strptime(rotation.date_debut, "%Y-%m-%d")
            end_date = datetime.strptime(rotation.date_fin, "%Y-%m-%d")
            current_date = start_date

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                if date_str not in service_concurrent_capacity[rotation.service_id]:
                    service_concurrent_capacity[rotation.service_id][date_str] = 0
                service_concurrent_capacity[rotation.service_id][date_str] += 1
                current_date += timedelta(days=1)

        # Check service capacity violations (concurrent capacity)
        for service in services:
            max_capacity = min(service.places_disponibles,
                               settings.max_concurrent_students)

            if service.id in service_concurrent_capacity:
                # Find maximum concurrent occupancy
                max_concurrent_occupancy = max(
                    service_concurrent_capacity[service.id].values())

                if max_concurrent_occupancy > max_capacity:
                    validation_results['critical_errors'].append(
                        f"Service {service.nom} exceeds concurrent capacity: {max_concurrent_occupancy} > {max_capacity}")

                # Count total assignments for utilization metrics
                total_assignments = len(
                    [r for r in rotations if r.service_id == service.id])
                logger.debug(
                    f"   📊 {service.nom}: {total_assignments} total assignments, max concurrent: {max_concurrent_occupancy}/{max_capacity}")
            else:
                validation_results['warnings'].append(
                    f"Service {service.nom} has no assignments")

        # 2. Student workload validation
        for etudiant in etudiants:
            student_rotations = student_assignments.get(etudiant.id, [])

            if len(student_rotations) == 0:
                validation_results['critical_errors'].append(
                    f"Student {etudiant.nom} {etudiant.prenom} has no assignments")
            elif len(student_rotations) < len(services) * 0.7:  # Less than 70% of services
                validation_results['warnings'].append(
                    f"Student {etudiant.nom} {etudiant.prenom} has few assignments: {len(student_rotations)}")

        # 3. Load balancing metrics
        # Calculate total assignments per service for load balancing
        service_total_assignments = {}
        for service in services:
            service_total_assignments[service.id] = len(
                [r for r in rotations if r.service_id == service.id])

        if service_total_assignments:
            assignment_values = list(service_total_assignments.values())
            avg_assignments = sum(assignment_values) / len(assignment_values)
            max_assignments = max(assignment_values)
            min_assignments = min(assignment_values)

            # Load balance score (lower is better)
            load_balance_score = (max_assignments - min_assignments) / \
                avg_assignments if avg_assignments > 0 else 0
            validation_results['metrics']['load_balance_score'] = load_balance_score

            if load_balance_score > 0.5:
                validation_results['warnings'].append(
                    f"Poor load balancing: score {load_balance_score:.2f}")

        # 4. Duration distribution validation
        total_duration = sum(
            (datetime.strptime(r.date_fin, "%Y-%m-%d") -
             datetime.strptime(r.date_debut, "%Y-%m-%d")).days + 1
            for r in rotations
        )
        avg_duration_per_student = total_duration / \
            len(etudiants) if etudiants else 0
        validation_results['metrics']['avg_duration_per_student'] = avg_duration_per_student

        # 5. Service utilization metrics
        service_utilization = {}
        for service in services:
            total_assignments = service_total_assignments.get(service.id, 0)
            max_possible_assignments = min(
                service.places_disponibles, settings.max_concurrent_students)

            # Calculate utilization based on total assignments vs theoretical maximum
            # This is a simplified utilization metric - more complex would consider time periods
            utilization = total_assignments / \
                len(etudiants) if len(etudiants) > 0 else 0
            service_utilization[service.id] = utilization

        avg_utilization = sum(service_utilization.values()) / \
            len(service_utilization) if service_utilization else 0
        validation_results['metrics']['avg_service_utilization'] = avg_utilization

        # 6. Calculate overall quality score
        quality_factors = []

        # No critical errors factor
        if not validation_results['critical_errors']:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.0)

        # Load balance factor (inverted, so lower balance score = higher quality)
        load_balance_score = validation_results['metrics'].get(
            'load_balance_score', 0.0)
        load_balance_factor = max(0, 1.0 - load_balance_score)
        quality_factors.append(load_balance_factor)

        # Service utilization factor
        utilization_factor = min(1.0, avg_utilization)
        quality_factors.append(utilization_factor)

        # Few warnings factor
        warnings_factor = max(
            0, 1.0 - len(validation_results['warnings']) * 0.1)
        quality_factors.append(warnings_factor)

        validation_results['quality_score'] = sum(
            quality_factors) / len(quality_factors)

        logger.debug(
            f"🎯 Validation completed with quality score: {validation_results['quality_score']:.2f}")
        return validation_results

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
