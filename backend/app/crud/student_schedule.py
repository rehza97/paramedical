from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
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
        
        # Calculate schedule metrics
        nb_services_total = len(rotations)
        duree_totale_jours = (datetime.strptime(date_fin_planning, "%Y-%m-%d") - 
                             datetime.strptime(date_debut_planning, "%Y-%m-%d")).days + 1
        
        # Create the main schedule
        db_schedule = StudentSchedule(
            id=str(uuid.uuid4()),
            etudiant_id=etudiant_id,
            planning_id=planning_id,
            date_debut_planning=date_debut_planning,
            date_fin_planning=date_fin_planning,
            nb_services_total=nb_services_total,
            duree_totale_jours=duree_totale_jours,
            statut="en_cours"
        )
        db.add(db_schedule)
        db.flush()
        
        # Create schedule details for each rotation
        for rotation_data in rotations:
            duree_jours = (datetime.strptime(rotation_data['date_fin'], "%Y-%m-%d") - 
                          datetime.strptime(rotation_data['date_debut'], "%Y-%m-%d")).days + 1
            
            schedule_detail = StudentScheduleDetail(
                id=str(uuid.uuid4()),
                schedule_id=db_schedule.id,
                rotation_id=rotation_data['id'],
                service_id=rotation_data['service_id'],
                service_nom=rotation_data['service_nom'],
                ordre_service=rotation_data['ordre'],
                date_debut=rotation_data['date_debut'],
                date_fin=rotation_data['date_fin'],
                duree_jours=duree_jours,
                statut="planifie"
            )
            db.add(schedule_detail)
        
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    
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
        
        # Find the schedule detail
        schedule_detail = db.query(StudentScheduleDetail).filter(
            StudentScheduleDetail.schedule_id == schedule_id,
            StudentScheduleDetail.service_id == service_id
        ).first()
        
        if not schedule_detail:
            raise HTTPException(status_code=404, detail="Service non trouvé dans le planning")
        
        # Update status and notes
        schedule_detail.statut = new_statut
        if notes:
            schedule_detail.notes = notes
        
        # Update actual dates if service is starting/completing
        if new_statut == "en_cours" and not schedule_detail.date_debut_reelle:
            schedule_detail.date_debut_reelle = datetime.now().strftime("%Y-%m-%d")
        elif new_statut == "termine" and not schedule_detail.date_fin_reelle:
            schedule_detail.date_fin_reelle = datetime.now().strftime("%Y-%m-%d")
        
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
            
            # Update overall status if all services are completed
            if completed_services == schedule.nb_services_total:
                schedule.statut = "termine"
        
        db.commit()
        db.refresh(schedule_detail)
        return schedule_detail
    
    def get_progress_summary(self, db: Session, *, etudiant_id: str) -> StudentScheduleProgress:
        """Get a comprehensive progress summary for a student"""
        
        # Get active schedule
        schedule = self.get_active_by_etudiant(db, etudiant_id=etudiant_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Aucun planning actif trouvé")
        
        # Get student info
        etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
        if not etudiant:
            raise HTTPException(status_code=404, detail="Étudiant non trouvé")
        
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
        
        for detail in details:
            service_name = detail.service_nom
            if detail.statut == "termine":
                services_completes.append(service_name)
            elif detail.statut == "en_cours":
                services_en_cours.append(service_name)
            elif detail.statut == "planifie":
                services_planifies.append(service_name)
                # Find the next planned service
                if not prochaine_service and detail.date_debut >= datetime.now().strftime("%Y-%m-%d"):
                    prochaine_service = service_name
                    date_prochaine_service = detail.date_debut
        
        # Calculate global progression
        progression_globale = (len(services_completes) / schedule.nb_services_total) * 100
        
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
        
        schedules = self.get_by_planning(db, planning_id=planning_id)
        summaries = []
        
        for schedule in schedules:
            # Get student info
            etudiant = db.query(Etudiant).filter(Etudiant.id == schedule.etudiant_id).first()
            if not etudiant:
                continue
            
            # Calculate progression
            progression = (schedule.nb_services_completes / schedule.nb_services_total) * 100
            
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
        schedule = self.get(db, id=schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Planning non trouvé")
        
        schedule.is_active = False
        schedule.date_modification = datetime.now()
        db.commit()
        db.refresh(schedule)
        return schedule
    
    def create_new_version(self, db: Session, *, schedule_id: str) -> StudentSchedule:
        """Create a new version of an existing schedule"""
        old_schedule = self.get(db, id=schedule_id)
        if not old_schedule:
            raise HTTPException(status_code=404, detail="Planning non trouvé")
        
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
            version=old_schedule.version + 1,
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

student_schedule = CRUDStudentSchedule(StudentSchedule) 
from sqlalchemy.orm import Session
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
        
        # Calculate schedule metrics
        nb_services_total = len(rotations)
        duree_totale_jours = (datetime.strptime(date_fin_planning, "%Y-%m-%d") - 
                             datetime.strptime(date_debut_planning, "%Y-%m-%d")).days + 1
        
        # Create the main schedule
        db_schedule = StudentSchedule(
            id=str(uuid.uuid4()),
            etudiant_id=etudiant_id,
            planning_id=planning_id,
            date_debut_planning=date_debut_planning,
            date_fin_planning=date_fin_planning,
            nb_services_total=nb_services_total,
            duree_totale_jours=duree_totale_jours,
            statut="en_cours"
        )
        db.add(db_schedule)
        db.flush()
        
        # Create schedule details for each rotation
        for rotation_data in rotations:
            duree_jours = (datetime.strptime(rotation_data['date_fin'], "%Y-%m-%d") - 
                          datetime.strptime(rotation_data['date_debut'], "%Y-%m-%d")).days + 1
            
            schedule_detail = StudentScheduleDetail(
                id=str(uuid.uuid4()),
                schedule_id=db_schedule.id,
                rotation_id=rotation_data['id'],
                service_id=rotation_data['service_id'],
                service_nom=rotation_data['service_nom'],
                ordre_service=rotation_data['ordre'],
                date_debut=rotation_data['date_debut'],
                date_fin=rotation_data['date_fin'],
                duree_jours=duree_jours,
                statut="planifie"
            )
            db.add(schedule_detail)
        
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    
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
        
        # Find the schedule detail
        schedule_detail = db.query(StudentScheduleDetail).filter(
            StudentScheduleDetail.schedule_id == schedule_id,
            StudentScheduleDetail.service_id == service_id
        ).first()
        
        if not schedule_detail:
            raise HTTPException(status_code=404, detail="Service non trouvé dans le planning")
        
        # Update status and notes
        schedule_detail.statut = new_statut
        if notes:
            schedule_detail.notes = notes
        
        # Update actual dates if service is starting/completing
        if new_statut == "en_cours" and not schedule_detail.date_debut_reelle:
            schedule_detail.date_debut_reelle = datetime.now().strftime("%Y-%m-%d")
        elif new_statut == "termine" and not schedule_detail.date_fin_reelle:
            schedule_detail.date_fin_reelle = datetime.now().strftime("%Y-%m-%d")
        
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
            
            # Update overall status if all services are completed
            if completed_services == schedule.nb_services_total:
                schedule.statut = "termine"
        
        db.commit()
        db.refresh(schedule_detail)
        return schedule_detail
    
    def get_progress_summary(self, db: Session, *, etudiant_id: str) -> StudentScheduleProgress:
        """Get a comprehensive progress summary for a student"""
        
        # Get active schedule
        schedule = self.get_active_by_etudiant(db, etudiant_id=etudiant_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Aucun planning actif trouvé")
        
        # Get student info
        etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
        if not etudiant:
            raise HTTPException(status_code=404, detail="Étudiant non trouvé")
        
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
        
        for detail in details:
            service_name = detail.service_nom
            if detail.statut == "termine":
                services_completes.append(service_name)
            elif detail.statut == "en_cours":
                services_en_cours.append(service_name)
            elif detail.statut == "planifie":
                services_planifies.append(service_name)
                # Find the next planned service
                if not prochaine_service and detail.date_debut >= datetime.now().strftime("%Y-%m-%d"):
                    prochaine_service = service_name
                    date_prochaine_service = detail.date_debut
        
        # Calculate global progression
        progression_globale = (len(services_completes) / schedule.nb_services_total) * 100
        
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
        
        schedules = self.get_by_planning(db, planning_id=planning_id)
        summaries = []
        
        for schedule in schedules:
            # Get student info
            etudiant = db.query(Etudiant).filter(Etudiant.id == schedule.etudiant_id).first()
            if not etudiant:
                continue
            
            # Calculate progression
            progression = (schedule.nb_services_completes / schedule.nb_services_total) * 100
            
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
        schedule = self.get(db, id=schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Planning non trouvé")
        
        schedule.is_active = False
        schedule.date_modification = datetime.now()
        db.commit()
        db.refresh(schedule)
        return schedule
    
    def create_new_version(self, db: Session, *, schedule_id: str) -> StudentSchedule:
        """Create a new version of an existing schedule"""
        old_schedule = self.get(db, id=schedule_id)
        if not old_schedule:
            raise HTTPException(status_code=404, detail="Planning non trouvé")
        
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
            version=old_schedule.version + 1,
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

student_schedule = CRUDStudentSchedule(StudentSchedule) 
 
 