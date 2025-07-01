from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from datetime import datetime, timedelta

from ..models import Planning, Promotion, Service, Rotation, Etudiant
from ..schemas import (
    PlanningEfficiencyAnalysis, 
    PlanningValidationResult, 
    ServiceOccupationStats,
    Planning as PlanningSchema,
    Rotation as RotationSchema
)

class AdvancedPlanningAlgorithm:
    """Advanced planning algorithm with intelligent load balancing"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_advanced_planning(
        self, promo_id: str, date_debut_str: str = "2025-01-01"
    ) -> Tuple[PlanningSchema, PlanningEfficiencyAnalysis, PlanningValidationResult]:
        """
        Generate planning using the advanced algorithm with efficiency analysis and validation
        """
        # Get promotion and services
        promotion = self.db.query(Promotion).filter(Promotion.id == promo_id).first()
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion non trouvée")
        
        services = self.db.query(Service).all()
        if not services:
            raise HTTPException(status_code=400, detail="Aucun service configuré")
        
        # Convert to dict format for algorithm
        promotion_dict = {
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
        
        services_list = [
            {
                'id': s.id,
                'nom': s.nom,
                'places_disponibles': s.places_disponibles,
                'duree_stage_jours': s.duree_stage_jours
            } for s in services
        ]
        
        # Delete existing planning
        self.db.query(Planning).filter(Planning.promo_id == promo_id).delete()
        
        # Generate planning using advanced algorithm
        planning_result = self._generer_algorithme_repartition(
            promotion_dict, services_list, date_debut_str
        )
        
        # Save to database
        db_planning = Planning(
            id=planning_result.id,
            promo_id=planning_result.promo_id
        )
        self.db.add(db_planning)
        self.db.flush()
        
        # Save rotations
        for rotation_data in planning_result.rotations:
            db_rotation = Rotation(
                id=str(uuid.uuid4()),
                etudiant_id=rotation_data.etudiant_id,
                service_id=rotation_data.service_id,
                date_debut=rotation_data.date_debut,
                date_fin=rotation_data.date_fin,
                ordre=rotation_data.ordre,
                planning_id=db_planning.id
            )
            self.db.add(db_rotation)
        
        self.db.commit()
        self.db.refresh(db_planning)
        
        # Create student schedules
        self._create_student_schedules(db_planning, planning_result)
        
        # Analyze efficiency
        efficiency_analysis = self._analyser_efficacite_planning(planning_result, services_list)
        
        # Validate planning
        validation_result = self._valider_planning(planning_result, services_list)
        
        # Convert to response format
        planning_response = self._convert_to_planning_response(db_planning)
        
        return planning_response, efficiency_analysis, validation_result
    
    def _create_student_schedules(self, db_planning: Planning, planning_result: PlanningSchema):
        """Create individual student schedules from the planning"""
        from .student_schedule import student_schedule
        
        # Group rotations by student
        rotations_par_etudiant = {}
        for rotation in planning_result.rotations:
            if rotation.etudiant_id not in rotations_par_etudiant:
                rotations_par_etudiant[rotation.etudiant_id] = []
            rotations_par_etudiant[rotation.etudiant_id].append(rotation)
        
        # Calculate overall planning dates
        all_dates_debut = [datetime.strptime(r.date_debut, "%Y-%m-%d") for r in planning_result.rotations]
        all_dates_fin = [datetime.strptime(r.date_fin, "%Y-%m-%d") for r in planning_result.rotations]
        
        date_debut_planning = min(all_dates_debut).strftime("%Y-%m-%d")
        date_fin_planning = max(all_dates_fin).strftime("%Y-%m-%d")
        
        # Create schedule for each student
        for etudiant_id, rotations in rotations_par_etudiant.items():
            # Convert rotations to dict format for schedule creation
            rotations_dict = []
            for rotation in rotations:
                rotation_dict = {
                    'id': rotation.id,
                    'service_id': rotation.service_id,
                    'service_nom': rotation.service_nom,
                    'ordre': rotation.ordre,
                    'date_debut': rotation.date_debut,
                    'date_fin': rotation.date_fin
                }
                rotations_dict.append(rotation_dict)
            
            # Create student schedule
            student_schedule.create_from_planning(
                db=self.db,
                planning_id=db_planning.id,
                etudiant_id=etudiant_id,
                rotations=rotations_dict,
                date_debut_planning=date_debut_planning,
                date_fin_planning=date_fin_planning
            )
    
    def _generer_algorithme_repartition(
        self, promotion: Dict, services: List[Dict], date_debut_str: str
    ) -> PlanningSchema:
        """
        Advanced automatic distribution algorithm with flexible order and intelligent balancing
        Ensures each student goes through all services with capacity optimization
        """
        etudiants = promotion['etudiants']
        nb_etudiants = len(etudiants)
        nb_services = len(services)
        
        if nb_services == 0:
            raise HTTPException(status_code=400, detail="Aucun service disponible")
        
        if nb_etudiants == 0:
            raise HTTPException(status_code=400, detail="Aucun étudiant dans la promotion")
        
        # Sort services by name for consistent reference order
        services_sorted = sorted(services, key=lambda x: x['nom'])
        
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
        rotations = []
        
        # Verify all services have valid capacity
        for service in services_sorted:
            if service['places_disponibles'] <= 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Service '{service['nom']}' n'a pas de places disponibles"
                )
        
        # Structure to track service occupation by date
        service_occupation = {}  # {service_id: {date: nombre_etudiants}}
        
        # Structure to track completed services by each student
        etudiant_services_completes = {}  # {etudiant_id: set(service_ids)}
        for etudiant in etudiants:
            etudiant_services_completes[etudiant['id']] = set()
        
        def get_occupation_service(service_id: str, date: datetime) -> int:
            """Returns the number of students in a service on a given date"""
            date_str = date.strftime("%Y-%m-%d")
            return service_occupation.get(service_id, {}).get(date_str, 0)
        
        def ajouter_occupation_service(service_id: str, date_debut: datetime, date_fin: datetime):
            """Adds a student's occupation in a service for a period"""
            if service_id not in service_occupation:
                service_occupation[service_id] = {}
            
            current_date = date_debut
            while current_date <= date_fin:
                date_str = current_date.strftime("%Y-%m-%d")
                service_occupation[service_id][date_str] = service_occupation[service_id].get(date_str, 0) + 1
                current_date += timedelta(days=1)
        
        def calculer_score_service(service: Dict, date_souhaitee: datetime) -> float:
            """
            Calculate a score to prioritize services (higher = better)
            Intelligent balancing: current availability + total capacity + urgency
            """
            service_id = service['id']
            capacite_totale = service['places_disponibles']
            duree_stage = service['duree_stage_jours']
            
            # 1. Immediate availability score (0-1)
            occupation_actuelle = get_occupation_service(service_id, date_souhaitee)
            places_libres = max(0, capacite_totale - occupation_actuelle)
            score_disponibilite = places_libres / capacite_totale if capacite_totale > 0 else 0
            
            # 2. Relative capacity score (services with more places = priority)
            capacite_max = max([s['places_disponibles'] for s in services_sorted])
            score_capacite = capacite_totale / capacite_max if capacite_max > 0 else 0
            
            # 3. Urgency score (bottlenecks have priority)
            score_urgence = (capacite_max - capacite_totale + 1) / capacite_max if capacite_max > 0 else 0
            
            # 4. Duration score (favor longer internships when possible)
            duree_max = max([s['duree_stage_jours'] for s in services_sorted])
            score_duree = duree_stage / duree_max if duree_max > 0 else 0
            
            # Weighted final score calculation
            score_final = (
                score_disponibilite * 0.4 +  # 40% - immediate availability
                score_capacite * 0.25 +      # 25% - total capacity
                score_urgence * 0.25 +       # 25% - urgency (bottlenecks)
                score_duree * 0.1            # 10% - internship duration
            )
            
            return score_final
        
        def trouver_meilleur_service_disponible(etudiant_id: str, date_souhaitee: datetime) -> Tuple:
            """
            Find the best available service for a student on a given date
            Returns (service, optimal_start_date) or (None, None) if no service available
            """
            services_restants = [
                s for s in services_sorted 
                if s['id'] not in etudiant_services_completes[etudiant_id]
            ]
            
            if not services_restants:
                return None, None
            
            meilleur_service = None
            meilleure_date = None
            meilleur_score = -1
            
            for service in services_restants:
                # Find next available date for this service
                duree_stage = service['duree_stage_jours']
                capacite = service['places_disponibles']
                
                # Search within a 90-day window
                for decalage in range(90):
                    date_candidate = date_souhaitee + timedelta(days=decalage)
                    
                    # Check if entire internship period is available
                    periode_libre = True
                    for jour in range(duree_stage):
                        date_jour = date_candidate + timedelta(days=jour)
                        if get_occupation_service(service['id'], date_jour) >= capacite:
                            periode_libre = False
                            break
                    
                    if periode_libre:
                        # Calculate score for this service at this date
                        score = calculer_score_service(service, date_candidate)
                        
                        # Penalize delays (favor closer dates)
                        penalite_decalage = max(0, 1 - (decalage / 30.0))
                        score_ajuste = score * penalite_decalage
                        
                        if score_ajuste > meilleur_score:
                            meilleur_score = score_ajuste
                            meilleur_service = service
                            meilleure_date = date_candidate
                        
                        break  # Take first available date for this service
            
            return meilleur_service, meilleure_date
        
        # Structure to track next available dates for each student
        etudiant_prochaine_date = {}
        for etudiant in etudiants:
            etudiant_prochaine_date[etudiant['id']] = date_debut
        
        # Main loop: assign until all students have all services
        tours_max = nb_etudiants * nb_services + 100  # Safety against infinite loops
        tour_actuel = 0
        
        while tour_actuel < tours_max:
            tour_actuel += 1
            
            # Check if all students are finished
            tous_termines = all(
                len(etudiant_services_completes[etudiant['id']]) == nb_services 
                for etudiant in etudiants
            )
            
            if tous_termines:
                break
            
            # For each student, try to assign their next service
            progres_ce_tour = False
            
            for etudiant in etudiants:
                etudiant_id = etudiant['id']
                
                # If this student has finished all services, skip
                if len(etudiant_services_completes[etudiant_id]) == nb_services:
                    continue
                
                # Find best available service for this student
                service, date_debut_stage = trouver_meilleur_service_disponible(
                    etudiant_id, 
                    etudiant_prochaine_date[etudiant_id]
                )
                
                if service is None:
                    # No service available, shift search date
                    etudiant_prochaine_date[etudiant_id] += timedelta(days=1)
                    continue
                
                # Assign student to this service
                date_fin_stage = date_debut_stage + timedelta(days=service['duree_stage_jours'] - 1)
                
                # Reserve place in service
                ajouter_occupation_service(service['id'], date_debut_stage, date_fin_stage)
                
                # Mark service as completed for this student
                etudiant_services_completes[etudiant_id].add(service['id'])
                
                # Calculate order (number of services already completed + 1)
                ordre = len(etudiant_services_completes[etudiant_id])
                
                # Create rotation
                rotation = RotationSchema(
                    id=str(uuid.uuid4()),
                    etudiant_id=etudiant['id'],
                    service_id=service['id'],
                    date_debut=date_debut_stage.strftime("%Y-%m-%d"),
                    date_fin=date_fin_stage.strftime("%Y-%m-%d"),
                    ordre=ordre,
                    planning_id="",  # Will be set later
                    etudiant_nom=f"{etudiant['prenom']} {etudiant['nom']}",
                    service_nom=service['nom']
                )
                rotations.append(rotation)
                
                # Update next available date for this student
                etudiant_prochaine_date[etudiant_id] = date_fin_stage + timedelta(days=1)
                
                progres_ce_tour = True
            
            # If no progress was made this round, there's a problem
            if not progres_ce_tour:
                # Shift all search dates by one day
                for etudiant_id in etudiant_prochaine_date:
                    etudiant_prochaine_date[etudiant_id] += timedelta(days=1)
        
        # Verify all students have all their services
        for etudiant in etudiants:
            if len(etudiant_services_completes[etudiant['id']]) != nb_services:
                raise HTTPException(
                    status_code=500,
                    detail=f"Impossible d'assigner tous les services à l'étudiant {etudiant['prenom']} {etudiant['nom']}"
                )
        
        # Create final planning
        planning = PlanningSchema(
            id=str(uuid.uuid4()),
            promo_id=promotion['id'],
            date_creation=datetime.now(),
            promo_nom=promotion['nom'],
            rotations=rotations
        )
        
        return planning
    
    def _analyser_efficacite_planning(
        self, planning: PlanningSchema, services: List[Dict]
    ) -> PlanningEfficiencyAnalysis:
        """Analyze the efficiency of the generated planning"""
        services_dict = {s['id']: s for s in services}
        
        # Calculate statistics
        dates_debut = [datetime.strptime(r.date_debut, "%Y-%m-%d") for r in planning.rotations]
        dates_fin = [datetime.strptime(r.date_fin, "%Y-%m-%d") for r in planning.rotations]
        
        date_debut_planning = min(dates_debut)
        date_fin_planning = max(dates_fin)
        duree_totale = (date_fin_planning - date_debut_planning).days + 1
        
        # Calculate average occupation rate per service
        occupation_par_service = {}
        for service in services:
            service_id = service['id']
            rotations_service = [r for r in planning.rotations if r.service_id == service_id]
            
            jours_occupation = {}
            for rotation in rotations_service:
                date_debut = datetime.strptime(rotation.date_debut, "%Y-%m-%d")
                date_fin = datetime.strptime(rotation.date_fin, "%Y-%m-%d")
                
                current_date = date_debut
                while current_date <= date_fin:
                    date_str = current_date.strftime("%Y-%m-%d")
                    jours_occupation[date_str] = jours_occupation.get(date_str, 0) + 1
                    current_date += timedelta(days=1)
            
            # Calculate average occupation rate
            if jours_occupation:
                occupation_moyenne = sum(jours_occupation.values()) / len(jours_occupation)
                taux_occupation = occupation_moyenne / service['places_disponibles']
            else:
                taux_occupation = 0
            
            occupation_par_service[service['nom']] = ServiceOccupationStats(
                taux_occupation=round(taux_occupation * 100, 1),
                jours_actifs=len(jours_occupation),
                occupation_moyenne=round(occupation_moyenne, 1)
            )
        
        return PlanningEfficiencyAnalysis(
            duree_totale_jours=duree_totale,
            date_debut=date_debut_planning.strftime("%Y-%m-%d"),
            date_fin=date_fin_planning.strftime("%Y-%m-%d"),
            nb_rotations=len(planning.rotations),
            occupation_services=occupation_par_service
        )
    
    def _valider_planning(self, planning: PlanningSchema, services: List[Dict]) -> PlanningValidationResult:
        """Validate a planning and return a list of errors if any"""
        erreurs = []
        services_dict = {s['id']: s for s in services}
        
        # Group rotations by service and date
        occupation_par_service = {}
        
        for rotation in planning.rotations:
            service_id = rotation.service_id
            if service_id not in occupation_par_service:
                occupation_par_service[service_id] = {}
            
            # Calculate all dates for this rotation
            date_debut = datetime.strptime(rotation.date_debut, "%Y-%m-%d")
            date_fin = datetime.strptime(rotation.date_fin, "%Y-%m-%d")
            
            current_date = date_debut
            while current_date <= date_fin:
                date_str = current_date.strftime("%Y-%m-%d")
                if date_str not in occupation_par_service[service_id]:
                    occupation_par_service[service_id][date_str] = []
                occupation_par_service[service_id][date_str].append(rotation.etudiant_nom)
                current_date += timedelta(days=1)
        
        # Check capacity overruns
        for service_id, dates_occupation in occupation_par_service.items():
            service = services_dict.get(service_id)
            if not service:
                continue
                
            capacite = service['places_disponibles']
            nom_service = service['nom']
            
            for date_str, etudiants in dates_occupation.items():
                if len(etudiants) > capacite:
                    erreurs.append(
                        f"Dépassement de capacité dans '{nom_service}' le {date_str}: "
                        f"{len(etudiants)} étudiants pour {capacite} places disponibles"
                    )
        
        # Check that each student has all services
        rotations_par_etudiant = {}
        for rotation in planning.rotations:
            if rotation.etudiant_id not in rotations_par_etudiant:
                rotations_par_etudiant[rotation.etudiant_id] = []
            rotations_par_etudiant[rotation.etudiant_id].append(rotation)
        
        for etudiant_id, rotations_etudiant in rotations_par_etudiant.items():
            services_etudiant = set(r.service_id for r in rotations_etudiant)
            services_requis = set(s['id'] for s in services)
            
            if services_etudiant != services_requis:
                services_manquants = services_requis - services_etudiant
                if services_manquants:
                    noms_manquants = [services_dict[sid]['nom'] for sid in services_manquants]
                    erreurs.append(
                        f"Étudiant {rotations_etudiant[0].etudiant_nom} n'a pas été assigné aux services: "
                        f"{', '.join(noms_manquants)}"
                    )
        
        return PlanningValidationResult(
            is_valid=len(erreurs) == 0,
            erreurs=erreurs
        )
    
    def _convert_to_planning_response(self, db_planning: Planning) -> PlanningSchema:
        """Convert database planning to response format"""
        planning_dict = {
            "id": db_planning.id,
            "promo_id": db_planning.promo_id,
            "date_creation": db_planning.date_creation,
            "promo_nom": db_planning.promotion.nom,
            "rotations": []
        }
        
        for rotation in db_planning.rotations:
            rotation_dict = RotationSchema(
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
            planning_dict["rotations"].append(rotation_dict)
        
        return PlanningSchema(**planning_dict)

# Create instance
def get_advanced_planning_algorithm(db: Session) -> AdvancedPlanningAlgorithm:
    return AdvancedPlanningAlgorithm(db) 
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from datetime import datetime, timedelta

from ..models import Planning, Promotion, Service, Rotation, Etudiant
from ..schemas import (
    PlanningEfficiencyAnalysis, 
    PlanningValidationResult, 
    ServiceOccupationStats,
    Planning as PlanningSchema,
    Rotation as RotationSchema
)

class AdvancedPlanningAlgorithm:
    """Advanced planning algorithm with intelligent load balancing"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_advanced_planning(
        self, promo_id: str, date_debut_str: str = "2025-01-01"
    ) -> Tuple[PlanningSchema, PlanningEfficiencyAnalysis, PlanningValidationResult]:
        """
        Generate planning using the advanced algorithm with efficiency analysis and validation
        """
        # Get promotion and services
        promotion = self.db.query(Promotion).filter(Promotion.id == promo_id).first()
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion non trouvée")
        
        services = self.db.query(Service).all()
        if not services:
            raise HTTPException(status_code=400, detail="Aucun service configuré")
        
        # Convert to dict format for algorithm
        promotion_dict = {
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
        
        services_list = [
            {
                'id': s.id,
                'nom': s.nom,
                'places_disponibles': s.places_disponibles,
                'duree_stage_jours': s.duree_stage_jours
            } for s in services
        ]
        
        # Delete existing planning
        self.db.query(Planning).filter(Planning.promo_id == promo_id).delete()
        
        # Generate planning using advanced algorithm
        planning_result = self._generer_algorithme_repartition(
            promotion_dict, services_list, date_debut_str
        )
        
        # Save to database
        db_planning = Planning(
            id=planning_result.id,
            promo_id=planning_result.promo_id
        )
        self.db.add(db_planning)
        self.db.flush()
        
        # Save rotations
        for rotation_data in planning_result.rotations:
            db_rotation = Rotation(
                id=str(uuid.uuid4()),
                etudiant_id=rotation_data.etudiant_id,
                service_id=rotation_data.service_id,
                date_debut=rotation_data.date_debut,
                date_fin=rotation_data.date_fin,
                ordre=rotation_data.ordre,
                planning_id=db_planning.id
            )
            self.db.add(db_rotation)
        
        self.db.commit()
        self.db.refresh(db_planning)
        
        # Create student schedules
        self._create_student_schedules(db_planning, planning_result)
        
        # Analyze efficiency
        efficiency_analysis = self._analyser_efficacite_planning(planning_result, services_list)
        
        # Validate planning
        validation_result = self._valider_planning(planning_result, services_list)
        
        # Convert to response format
        planning_response = self._convert_to_planning_response(db_planning)
        
        return planning_response, efficiency_analysis, validation_result
    
    def _create_student_schedules(self, db_planning: Planning, planning_result: PlanningSchema):
        """Create individual student schedules from the planning"""
        from .student_schedule import student_schedule
        
        # Group rotations by student
        rotations_par_etudiant = {}
        for rotation in planning_result.rotations:
            if rotation.etudiant_id not in rotations_par_etudiant:
                rotations_par_etudiant[rotation.etudiant_id] = []
            rotations_par_etudiant[rotation.etudiant_id].append(rotation)
        
        # Calculate overall planning dates
        all_dates_debut = [datetime.strptime(r.date_debut, "%Y-%m-%d") for r in planning_result.rotations]
        all_dates_fin = [datetime.strptime(r.date_fin, "%Y-%m-%d") for r in planning_result.rotations]
        
        date_debut_planning = min(all_dates_debut).strftime("%Y-%m-%d")
        date_fin_planning = max(all_dates_fin).strftime("%Y-%m-%d")
        
        # Create schedule for each student
        for etudiant_id, rotations in rotations_par_etudiant.items():
            # Convert rotations to dict format for schedule creation
            rotations_dict = []
            for rotation in rotations:
                rotation_dict = {
                    'id': rotation.id,
                    'service_id': rotation.service_id,
                    'service_nom': rotation.service_nom,
                    'ordre': rotation.ordre,
                    'date_debut': rotation.date_debut,
                    'date_fin': rotation.date_fin
                }
                rotations_dict.append(rotation_dict)
            
            # Create student schedule
            student_schedule.create_from_planning(
                db=self.db,
                planning_id=db_planning.id,
                etudiant_id=etudiant_id,
                rotations=rotations_dict,
                date_debut_planning=date_debut_planning,
                date_fin_planning=date_fin_planning
            )
    
    def _generer_algorithme_repartition(
        self, promotion: Dict, services: List[Dict], date_debut_str: str
    ) -> PlanningSchema:
        """
        Advanced automatic distribution algorithm with flexible order and intelligent balancing
        Ensures each student goes through all services with capacity optimization
        """
        etudiants = promotion['etudiants']
        nb_etudiants = len(etudiants)
        nb_services = len(services)
        
        if nb_services == 0:
            raise HTTPException(status_code=400, detail="Aucun service disponible")
        
        if nb_etudiants == 0:
            raise HTTPException(status_code=400, detail="Aucun étudiant dans la promotion")
        
        # Sort services by name for consistent reference order
        services_sorted = sorted(services, key=lambda x: x['nom'])
        
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
        rotations = []
        
        # Verify all services have valid capacity
        for service in services_sorted:
            if service['places_disponibles'] <= 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Service '{service['nom']}' n'a pas de places disponibles"
                )
        
        # Structure to track service occupation by date
        service_occupation = {}  # {service_id: {date: nombre_etudiants}}
        
        # Structure to track completed services by each student
        etudiant_services_completes = {}  # {etudiant_id: set(service_ids)}
        for etudiant in etudiants:
            etudiant_services_completes[etudiant['id']] = set()
        
        def get_occupation_service(service_id: str, date: datetime) -> int:
            """Returns the number of students in a service on a given date"""
            date_str = date.strftime("%Y-%m-%d")
            return service_occupation.get(service_id, {}).get(date_str, 0)
        
        def ajouter_occupation_service(service_id: str, date_debut: datetime, date_fin: datetime):
            """Adds a student's occupation in a service for a period"""
            if service_id not in service_occupation:
                service_occupation[service_id] = {}
            
            current_date = date_debut
            while current_date <= date_fin:
                date_str = current_date.strftime("%Y-%m-%d")
                service_occupation[service_id][date_str] = service_occupation[service_id].get(date_str, 0) + 1
                current_date += timedelta(days=1)
        
        def calculer_score_service(service: Dict, date_souhaitee: datetime) -> float:
            """
            Calculate a score to prioritize services (higher = better)
            Intelligent balancing: current availability + total capacity + urgency
            """
            service_id = service['id']
            capacite_totale = service['places_disponibles']
            duree_stage = service['duree_stage_jours']
            
            # 1. Immediate availability score (0-1)
            occupation_actuelle = get_occupation_service(service_id, date_souhaitee)
            places_libres = max(0, capacite_totale - occupation_actuelle)
            score_disponibilite = places_libres / capacite_totale if capacite_totale > 0 else 0
            
            # 2. Relative capacity score (services with more places = priority)
            capacite_max = max([s['places_disponibles'] for s in services_sorted])
            score_capacite = capacite_totale / capacite_max if capacite_max > 0 else 0
            
            # 3. Urgency score (bottlenecks have priority)
            score_urgence = (capacite_max - capacite_totale + 1) / capacite_max if capacite_max > 0 else 0
            
            # 4. Duration score (favor longer internships when possible)
            duree_max = max([s['duree_stage_jours'] for s in services_sorted])
            score_duree = duree_stage / duree_max if duree_max > 0 else 0
            
            # Weighted final score calculation
            score_final = (
                score_disponibilite * 0.4 +  # 40% - immediate availability
                score_capacite * 0.25 +      # 25% - total capacity
                score_urgence * 0.25 +       # 25% - urgency (bottlenecks)
                score_duree * 0.1            # 10% - internship duration
            )
            
            return score_final
        
        def trouver_meilleur_service_disponible(etudiant_id: str, date_souhaitee: datetime) -> Tuple:
            """
            Find the best available service for a student on a given date
            Returns (service, optimal_start_date) or (None, None) if no service available
            """
            services_restants = [
                s for s in services_sorted 
                if s['id'] not in etudiant_services_completes[etudiant_id]
            ]
            
            if not services_restants:
                return None, None
            
            meilleur_service = None
            meilleure_date = None
            meilleur_score = -1
            
            for service in services_restants:
                # Find next available date for this service
                duree_stage = service['duree_stage_jours']
                capacite = service['places_disponibles']
                
                # Search within a 90-day window
                for decalage in range(90):
                    date_candidate = date_souhaitee + timedelta(days=decalage)
                    
                    # Check if entire internship period is available
                    periode_libre = True
                    for jour in range(duree_stage):
                        date_jour = date_candidate + timedelta(days=jour)
                        if get_occupation_service(service['id'], date_jour) >= capacite:
                            periode_libre = False
                            break
                    
                    if periode_libre:
                        # Calculate score for this service at this date
                        score = calculer_score_service(service, date_candidate)
                        
                        # Penalize delays (favor closer dates)
                        penalite_decalage = max(0, 1 - (decalage / 30.0))
                        score_ajuste = score * penalite_decalage
                        
                        if score_ajuste > meilleur_score:
                            meilleur_score = score_ajuste
                            meilleur_service = service
                            meilleure_date = date_candidate
                        
                        break  # Take first available date for this service
            
            return meilleur_service, meilleure_date
        
        # Structure to track next available dates for each student
        etudiant_prochaine_date = {}
        for etudiant in etudiants:
            etudiant_prochaine_date[etudiant['id']] = date_debut
        
        # Main loop: assign until all students have all services
        tours_max = nb_etudiants * nb_services + 100  # Safety against infinite loops
        tour_actuel = 0
        
        while tour_actuel < tours_max:
            tour_actuel += 1
            
            # Check if all students are finished
            tous_termines = all(
                len(etudiant_services_completes[etudiant['id']]) == nb_services 
                for etudiant in etudiants
            )
            
            if tous_termines:
                break
            
            # For each student, try to assign their next service
            progres_ce_tour = False
            
            for etudiant in etudiants:
                etudiant_id = etudiant['id']
                
                # If this student has finished all services, skip
                if len(etudiant_services_completes[etudiant_id]) == nb_services:
                    continue
                
                # Find best available service for this student
                service, date_debut_stage = trouver_meilleur_service_disponible(
                    etudiant_id, 
                    etudiant_prochaine_date[etudiant_id]
                )
                
                if service is None:
                    # No service available, shift search date
                    etudiant_prochaine_date[etudiant_id] += timedelta(days=1)
                    continue
                
                # Assign student to this service
                date_fin_stage = date_debut_stage + timedelta(days=service['duree_stage_jours'] - 1)
                
                # Reserve place in service
                ajouter_occupation_service(service['id'], date_debut_stage, date_fin_stage)
                
                # Mark service as completed for this student
                etudiant_services_completes[etudiant_id].add(service['id'])
                
                # Calculate order (number of services already completed + 1)
                ordre = len(etudiant_services_completes[etudiant_id])
                
                # Create rotation
                rotation = RotationSchema(
                    id=str(uuid.uuid4()),
                    etudiant_id=etudiant['id'],
                    service_id=service['id'],
                    date_debut=date_debut_stage.strftime("%Y-%m-%d"),
                    date_fin=date_fin_stage.strftime("%Y-%m-%d"),
                    ordre=ordre,
                    planning_id="",  # Will be set later
                    etudiant_nom=f"{etudiant['prenom']} {etudiant['nom']}",
                    service_nom=service['nom']
                )
                rotations.append(rotation)
                
                # Update next available date for this student
                etudiant_prochaine_date[etudiant_id] = date_fin_stage + timedelta(days=1)
                
                progres_ce_tour = True
            
            # If no progress was made this round, there's a problem
            if not progres_ce_tour:
                # Shift all search dates by one day
                for etudiant_id in etudiant_prochaine_date:
                    etudiant_prochaine_date[etudiant_id] += timedelta(days=1)
        
        # Verify all students have all their services
        for etudiant in etudiants:
            if len(etudiant_services_completes[etudiant['id']]) != nb_services:
                raise HTTPException(
                    status_code=500,
                    detail=f"Impossible d'assigner tous les services à l'étudiant {etudiant['prenom']} {etudiant['nom']}"
                )
        
        # Create final planning
        planning = PlanningSchema(
            id=str(uuid.uuid4()),
            promo_id=promotion['id'],
            date_creation=datetime.now(),
            promo_nom=promotion['nom'],
            rotations=rotations
        )
        
        return planning
    
    def _analyser_efficacite_planning(
        self, planning: PlanningSchema, services: List[Dict]
    ) -> PlanningEfficiencyAnalysis:
        """Analyze the efficiency of the generated planning"""
        services_dict = {s['id']: s for s in services}
        
        # Calculate statistics
        dates_debut = [datetime.strptime(r.date_debut, "%Y-%m-%d") for r in planning.rotations]
        dates_fin = [datetime.strptime(r.date_fin, "%Y-%m-%d") for r in planning.rotations]
        
        date_debut_planning = min(dates_debut)
        date_fin_planning = max(dates_fin)
        duree_totale = (date_fin_planning - date_debut_planning).days + 1
        
        # Calculate average occupation rate per service
        occupation_par_service = {}
        for service in services:
            service_id = service['id']
            rotations_service = [r for r in planning.rotations if r.service_id == service_id]
            
            jours_occupation = {}
            for rotation in rotations_service:
                date_debut = datetime.strptime(rotation.date_debut, "%Y-%m-%d")
                date_fin = datetime.strptime(rotation.date_fin, "%Y-%m-%d")
                
                current_date = date_debut
                while current_date <= date_fin:
                    date_str = current_date.strftime("%Y-%m-%d")
                    jours_occupation[date_str] = jours_occupation.get(date_str, 0) + 1
                    current_date += timedelta(days=1)
            
            # Calculate average occupation rate
            if jours_occupation:
                occupation_moyenne = sum(jours_occupation.values()) / len(jours_occupation)
                taux_occupation = occupation_moyenne / service['places_disponibles']
            else:
                taux_occupation = 0
            
            occupation_par_service[service['nom']] = ServiceOccupationStats(
                taux_occupation=round(taux_occupation * 100, 1),
                jours_actifs=len(jours_occupation),
                occupation_moyenne=round(occupation_moyenne, 1)
            )
        
        return PlanningEfficiencyAnalysis(
            duree_totale_jours=duree_totale,
            date_debut=date_debut_planning.strftime("%Y-%m-%d"),
            date_fin=date_fin_planning.strftime("%Y-%m-%d"),
            nb_rotations=len(planning.rotations),
            occupation_services=occupation_par_service
        )
    
    def _valider_planning(self, planning: PlanningSchema, services: List[Dict]) -> PlanningValidationResult:
        """Validate a planning and return a list of errors if any"""
        erreurs = []
        services_dict = {s['id']: s for s in services}
        
        # Group rotations by service and date
        occupation_par_service = {}
        
        for rotation in planning.rotations:
            service_id = rotation.service_id
            if service_id not in occupation_par_service:
                occupation_par_service[service_id] = {}
            
            # Calculate all dates for this rotation
            date_debut = datetime.strptime(rotation.date_debut, "%Y-%m-%d")
            date_fin = datetime.strptime(rotation.date_fin, "%Y-%m-%d")
            
            current_date = date_debut
            while current_date <= date_fin:
                date_str = current_date.strftime("%Y-%m-%d")
                if date_str not in occupation_par_service[service_id]:
                    occupation_par_service[service_id][date_str] = []
                occupation_par_service[service_id][date_str].append(rotation.etudiant_nom)
                current_date += timedelta(days=1)
        
        # Check capacity overruns
        for service_id, dates_occupation in occupation_par_service.items():
            service = services_dict.get(service_id)
            if not service:
                continue
                
            capacite = service['places_disponibles']
            nom_service = service['nom']
            
            for date_str, etudiants in dates_occupation.items():
                if len(etudiants) > capacite:
                    erreurs.append(
                        f"Dépassement de capacité dans '{nom_service}' le {date_str}: "
                        f"{len(etudiants)} étudiants pour {capacite} places disponibles"
                    )
        
        # Check that each student has all services
        rotations_par_etudiant = {}
        for rotation in planning.rotations:
            if rotation.etudiant_id not in rotations_par_etudiant:
                rotations_par_etudiant[rotation.etudiant_id] = []
            rotations_par_etudiant[rotation.etudiant_id].append(rotation)
        
        for etudiant_id, rotations_etudiant in rotations_par_etudiant.items():
            services_etudiant = set(r.service_id for r in rotations_etudiant)
            services_requis = set(s['id'] for s in services)
            
            if services_etudiant != services_requis:
                services_manquants = services_requis - services_etudiant
                if services_manquants:
                    noms_manquants = [services_dict[sid]['nom'] for sid in services_manquants]
                    erreurs.append(
                        f"Étudiant {rotations_etudiant[0].etudiant_nom} n'a pas été assigné aux services: "
                        f"{', '.join(noms_manquants)}"
                    )
        
        return PlanningValidationResult(
            is_valid=len(erreurs) == 0,
            erreurs=erreurs
        )
    
    def _convert_to_planning_response(self, db_planning: Planning) -> PlanningSchema:
        """Convert database planning to response format"""
        planning_dict = {
            "id": db_planning.id,
            "promo_id": db_planning.promo_id,
            "date_creation": db_planning.date_creation,
            "promo_nom": db_planning.promotion.nom,
            "rotations": []
        }
        
        for rotation in db_planning.rotations:
            rotation_dict = RotationSchema(
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
            planning_dict["rotations"].append(rotation_dict)
        
        return PlanningSchema(**planning_dict)

# Create instance
def get_advanced_planning_algorithm(db: Session) -> AdvancedPlanningAlgorithm:
    return AdvancedPlanningAlgorithm(db) 
 
 