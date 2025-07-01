from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from datetime import datetime, timedelta

from .base import CRUDBase
from ..models import Planning, Promotion, Service, Rotation, Etudiant
from ..schemas import PlanningCreate, PlanningBase

class CRUDPlanning(CRUDBase[Planning, PlanningCreate, PlanningBase]):
    def get_by_promotion(self, db: Session, *, promo_id: str) -> Optional[Planning]:
        """Get planning for a promotion"""
        return db.query(Planning).filter(Planning.promo_id == promo_id).first()

    def generate_planning(
        self, db: Session, *, promo_id: str, date_debut: str = "2025-01-01"
    ) -> Planning:
        """Generate planning for a promotion"""
        # Get promotion and services
        promotion = db.query(Promotion).filter(Promotion.id == promo_id).first()
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion non trouvée")
        
        services = db.query(Service).all()
        if not services:
            raise HTTPException(status_code=400, detail="Aucun service configuré")
        
        # Delete existing planning
        db.query(Planning).filter(Planning.promo_id == promo_id).delete()
        
        # Generate new planning
        planning = self._generate_algorithm(db, promotion, services, date_debut)
        return planning

    def _generate_algorithm(
        self, db: Session, promotion: Promotion, services: List[Service], date_debut_str: str
    ) -> Planning:
        """
        Algorithm for automatic stage distribution - PostgreSQL version
        Ensures each student goes through all services
        """
        etudiants = promotion.etudiants
        nb_etudiants = len(etudiants)
        nb_services = len(services)
        
        if nb_services == 0:
            raise HTTPException(status_code=400, detail="Aucun service disponible")
        
        # Sort services by name for consistent order
        services_sorted = sorted(services, key=lambda x: x.nom)
        
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
        
        # Create planning
        db_planning = Planning(
            id=str(uuid.uuid4()),
            promo_id=promotion.id
        )
        db.add(db_planning)
        db.flush()  # Get the planning ID
        
        # For each student, create their complete sequence of stages
        for idx_etudiant, etudiant in enumerate(etudiants):
            date_debut_etudiant = date_debut
            
            # Offset start date to avoid all students starting at the same time
            min_places = min([s.places_disponibles for s in services_sorted])
            decalage_jours = (idx_etudiant // min_places) * 7  # New group every 7 days
            date_debut_etudiant = date_debut + timedelta(days=decalage_jours)
            
            # For this student, create a rotation in each service
            date_courante_etudiant = date_debut_etudiant
            
            for ordre_service, service in enumerate(services_sorted):
                duree_jours = service.duree_stage_jours
                
                date_fin_stage = date_courante_etudiant + timedelta(days=duree_jours - 1)
                
                rotation = Rotation(
                    id=str(uuid.uuid4()),
                    etudiant_id=etudiant.id,
                    service_id=service.id,
                    date_debut=date_courante_etudiant.strftime("%Y-%m-%d"),
                    date_fin=date_fin_stage.strftime("%Y-%m-%d"),
                    ordre=ordre_service + 1,
                    planning_id=db_planning.id
                )
                db.add(rotation)
                
                # Move to end date + 1 day for next service
                date_courante_etudiant = date_fin_stage + timedelta(days=1)
        
        db.commit()
        
        # Return the planning with all relationships loaded
        db.refresh(db_planning)
        return db_planning

    def get_student_planning(
        self, db: Session, *, promo_id: str, etudiant_id: str
    ) -> List[Rotation]:
        """Get planning for a specific student"""
        planning = self.get_by_promotion(db, promo_id=promo_id)
        if not planning:
            raise HTTPException(status_code=404, detail="Planning non trouvé")
        
        rotations = db.query(Rotation).filter(
            Rotation.planning_id == planning.id,
            Rotation.etudiant_id == etudiant_id
        ).order_by(Rotation.ordre).all()
        
        return rotations

planning = CRUDPlanning(Planning) 
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from datetime import datetime, timedelta

from .base import CRUDBase
from ..models import Planning, Promotion, Service, Rotation, Etudiant
from ..schemas import PlanningCreate, PlanningBase

class CRUDPlanning(CRUDBase[Planning, PlanningCreate, PlanningBase]):
    def get_by_promotion(self, db: Session, *, promo_id: str) -> Optional[Planning]:
        """Get planning for a promotion"""
        return db.query(Planning).filter(Planning.promo_id == promo_id).first()

    def generate_planning(
        self, db: Session, *, promo_id: str, date_debut: str = "2025-01-01"
    ) -> Planning:
        """Generate planning for a promotion"""
        # Get promotion and services
        promotion = db.query(Promotion).filter(Promotion.id == promo_id).first()
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion non trouvée")
        
        services = db.query(Service).all()
        if not services:
            raise HTTPException(status_code=400, detail="Aucun service configuré")
        
        # Delete existing planning
        db.query(Planning).filter(Planning.promo_id == promo_id).delete()
        
        # Generate new planning
        planning = self._generate_algorithm(db, promotion, services, date_debut)
        return planning

    def _generate_algorithm(
        self, db: Session, promotion: Promotion, services: List[Service], date_debut_str: str
    ) -> Planning:
        """
        Algorithm for automatic stage distribution - PostgreSQL version
        Ensures each student goes through all services
        """
        etudiants = promotion.etudiants
        nb_etudiants = len(etudiants)
        nb_services = len(services)
        
        if nb_services == 0:
            raise HTTPException(status_code=400, detail="Aucun service disponible")
        
        # Sort services by name for consistent order
        services_sorted = sorted(services, key=lambda x: x.nom)
        
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
        
        # Create planning
        db_planning = Planning(
            id=str(uuid.uuid4()),
            promo_id=promotion.id
        )
        db.add(db_planning)
        db.flush()  # Get the planning ID
        
        # For each student, create their complete sequence of stages
        for idx_etudiant, etudiant in enumerate(etudiants):
            date_debut_etudiant = date_debut
            
            # Offset start date to avoid all students starting at the same time
            min_places = min([s.places_disponibles for s in services_sorted])
            decalage_jours = (idx_etudiant // min_places) * 7  # New group every 7 days
            date_debut_etudiant = date_debut + timedelta(days=decalage_jours)
            
            # For this student, create a rotation in each service
            date_courante_etudiant = date_debut_etudiant
            
            for ordre_service, service in enumerate(services_sorted):
                duree_jours = service.duree_stage_jours
                
                date_fin_stage = date_courante_etudiant + timedelta(days=duree_jours - 1)
                
                rotation = Rotation(
                    id=str(uuid.uuid4()),
                    etudiant_id=etudiant.id,
                    service_id=service.id,
                    date_debut=date_courante_etudiant.strftime("%Y-%m-%d"),
                    date_fin=date_fin_stage.strftime("%Y-%m-%d"),
                    ordre=ordre_service + 1,
                    planning_id=db_planning.id
                )
                db.add(rotation)
                
                # Move to end date + 1 day for next service
                date_courante_etudiant = date_fin_stage + timedelta(days=1)
        
        db.commit()
        
        # Return the planning with all relationships loaded
        db.refresh(db_planning)
        return db_planning

    def get_student_planning(
        self, db: Session, *, promo_id: str, etudiant_id: str
    ) -> List[Rotation]:
        """Get planning for a specific student"""
        planning = self.get_by_promotion(db, promo_id=promo_id)
        if not planning:
            raise HTTPException(status_code=404, detail="Planning non trouvé")
        
        rotations = db.query(Rotation).filter(
            Rotation.planning_id == planning.id,
            Rotation.etudiant_id == etudiant_id
        ).order_by(Rotation.ordre).all()
        
        return rotations

planning = CRUDPlanning(Planning) 
 
 