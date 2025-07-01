from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import Speciality
from ..schemas import SpecialityCreate, SpecialityBase

class CRUDSpeciality(CRUDBase[Speciality, SpecialityCreate, SpecialityBase]):
    def create_with_validation(
        self, db: Session, *, obj_in: SpecialityCreate
    ) -> Speciality:
        """Create a speciality with validation"""
        # Validation: duree_annees must be 3, 4, or 5
        if obj_in.duree_annees not in [3, 4, 5]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="La durée doit être de 3, 4 ou 5 années."
            )
        
        db_speciality = Speciality(
            id=str(uuid.uuid4()),
            nom=obj_in.nom,
            description=obj_in.description,
            duree_annees=obj_in.duree_annees
        )
        db.add(db_speciality)
        
        try:
            db.commit()
            db.refresh(db_speciality)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Le nom de la spécialité doit être unique."
            )
        
        return db_speciality

    def update_with_validation(
        self, db: Session, *, db_obj: Speciality, obj_in: SpecialityCreate
    ) -> Speciality:
        """Update a speciality with validation"""
        # Validation: duree_annees must be 3, 4, or 5
        if obj_in.duree_annees not in [3, 4, 5]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="La durée doit être de 3, 4 ou 5 années."
            )
        
        db_obj.nom = obj_in.nom
        db_obj.description = obj_in.description
        db_obj.duree_annees = obj_in.duree_annees
        
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Le nom de la spécialité doit être unique."
            )
        
        return db_obj

speciality = CRUDSpeciality(Speciality) 
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import Speciality
from ..schemas import SpecialityCreate, SpecialityBase

class CRUDSpeciality(CRUDBase[Speciality, SpecialityCreate, SpecialityBase]):
    def create_with_validation(
        self, db: Session, *, obj_in: SpecialityCreate
    ) -> Speciality:
        """Create a speciality with validation"""
        # Validation: duree_annees must be 3, 4, or 5
        if obj_in.duree_annees not in [3, 4, 5]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="La durée doit être de 3, 4 ou 5 années."
            )
        
        db_speciality = Speciality(
            id=str(uuid.uuid4()),
            nom=obj_in.nom,
            description=obj_in.description,
            duree_annees=obj_in.duree_annees
        )
        db.add(db_speciality)
        
        try:
            db.commit()
            db.refresh(db_speciality)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Le nom de la spécialité doit être unique."
            )
        
        return db_speciality

    def update_with_validation(
        self, db: Session, *, db_obj: Speciality, obj_in: SpecialityCreate
    ) -> Speciality:
        """Update a speciality with validation"""
        # Validation: duree_annees must be 3, 4, or 5
        if obj_in.duree_annees not in [3, 4, 5]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="La durée doit être de 3, 4 ou 5 années."
            )
        
        db_obj.nom = obj_in.nom
        db_obj.description = obj_in.description
        db_obj.duree_annees = obj_in.duree_annees
        
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Le nom de la spécialité doit être unique."
            )
        
        return db_obj

speciality = CRUDSpeciality(Speciality) 
 
 