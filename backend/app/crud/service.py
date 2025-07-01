from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import Service
from ..schemas import ServiceCreate, ServiceBase

class CRUDService(CRUDBase[Service, ServiceCreate, ServiceBase]):
    def create_with_validation(
        self, db: Session, *, obj_in: ServiceCreate
    ) -> Service:
        """Create a service with validation"""
        # Validation: places_disponibles and duree_stage_jours must be positive
        if obj_in.places_disponibles < 1 or obj_in.duree_stage_jours < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Les valeurs doivent être positives et supérieures à zéro."
            )
        
        db_service = Service(
            id=str(uuid.uuid4()),
            nom=obj_in.nom,
            places_disponibles=obj_in.places_disponibles,
            duree_stage_jours=obj_in.duree_stage_jours
        )
        db.add(db_service)
        
        try:
            db.commit()
            db.refresh(db_service)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Le nom du service doit être unique."
            )
        
        return db_service

    def update_with_validation(
        self, db: Session, *, db_obj: Service, obj_in: ServiceCreate
    ) -> Service:
        """Update a service with validation"""
        # Validation: places_disponibles and duree_stage_jours must be positive
        if obj_in.places_disponibles < 1 or obj_in.duree_stage_jours < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Les valeurs doivent être positives et supérieures à zéro."
            )
        
        db_obj.nom = obj_in.nom
        db_obj.places_disponibles = obj_in.places_disponibles
        db_obj.duree_stage_jours = obj_in.duree_stage_jours
        
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Le nom du service doit être unique."
            )
        
        return db_obj

    def delete_with_cascade(self, db: Session, *, id: str) -> Service:
        """Delete service and handle all associated data"""
        service_obj = self.get(db=db, id=id)
        if not service_obj:
            raise HTTPException(status_code=404, detail="Service non trouvé")
        
        # Delete in correct order to avoid foreign key violations
        from ..models import Rotation, StudentScheduleDetail
        
        # Delete student schedule details that reference rotations using this service
        db.query(StudentScheduleDetail).filter(StudentScheduleDetail.service_id == id).delete()
        
        # Delete rotations that use this service
        db.query(Rotation).filter(Rotation.service_id == id).delete()
        
        # Delete the service
        db.delete(service_obj)
        db.commit()
        return service_obj

service = CRUDService(Service) 
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import Service
from ..schemas import ServiceCreate, ServiceBase

class CRUDService(CRUDBase[Service, ServiceCreate, ServiceBase]):
    def create_with_validation(
        self, db: Session, *, obj_in: ServiceCreate
    ) -> Service:
        """Create a service with validation"""
        # Validation: places_disponibles and duree_stage_jours must be positive
        if obj_in.places_disponibles < 1 or obj_in.duree_stage_jours < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Les valeurs doivent être positives et supérieures à zéro."
            )
        
        db_service = Service(
            id=str(uuid.uuid4()),
            nom=obj_in.nom,
            places_disponibles=obj_in.places_disponibles,
            duree_stage_jours=obj_in.duree_stage_jours
        )
        db.add(db_service)
        
        try:
            db.commit()
            db.refresh(db_service)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Le nom du service doit être unique."
            )
        
        return db_service

    def update_with_validation(
        self, db: Session, *, db_obj: Service, obj_in: ServiceCreate
    ) -> Service:
        """Update a service with validation"""
        # Validation: places_disponibles and duree_stage_jours must be positive
        if obj_in.places_disponibles < 1 or obj_in.duree_stage_jours < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Les valeurs doivent être positives et supérieures à zéro."
            )
        
        db_obj.nom = obj_in.nom
        db_obj.places_disponibles = obj_in.places_disponibles
        db_obj.duree_stage_jours = obj_in.duree_stage_jours
        
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Le nom du service doit être unique."
            )
        
        return db_obj

    def delete_with_cascade(self, db: Session, *, id: str) -> Service:
        """Delete service and handle all associated data"""
        service_obj = self.get(db=db, id=id)
        if not service_obj:
            raise HTTPException(status_code=404, detail="Service non trouvé")
        
        # Delete in correct order to avoid foreign key violations
        from ..models import Rotation, StudentScheduleDetail
        
        # Delete student schedule details that reference rotations using this service
        db.query(StudentScheduleDetail).filter(StudentScheduleDetail.service_id == id).delete()
        
        # Delete rotations that use this service
        db.query(Rotation).filter(Rotation.service_id == id).delete()
        
        # Delete the service
        db.delete(service_obj)
        db.commit()
        return service_obj

service = CRUDService(Service) 
 
 