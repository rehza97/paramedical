from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import Service, Speciality
from ..schemas import ServiceCreate, ServiceBase
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context


class CRUDService(CRUDBase[Service, ServiceCreate, ServiceBase]):
    def get_by_speciality(self, db: Session, *, speciality_id: str) -> List[Service]:
        return db.query(Service).filter(Service.speciality_id == speciality_id).all()

    def create_with_validation(
        self, db: Session, *, obj_in: ServiceCreate
    ) -> Service:
        # Validate speciality exists
        speciality = db.query(Speciality).filter(
            Speciality.id == obj_in.speciality_id).first()
        if not speciality:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spécialité non trouvée"
            )

        # Validate name
        validate_string_length(obj_in.nom, "nom du service", 2, 200)

        # Validate duration
        if obj_in.duree_stage_jours < 1 or obj_in.duree_stage_jours > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La durée du stage doit être entre 1 et 365 jours"
            )

        # Validate capacity
        if obj_in.places_disponibles < 1 or obj_in.places_disponibles > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nombre de places doit être entre 1 et 100"
            )

        # Check for duplicate service name in same speciality
        existing_service = db.query(Service).filter(
            Service.nom == obj_in.nom,
            Service.speciality_id == obj_in.speciality_id
        ).first()

        if existing_service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un service avec ce nom existe déjà dans cette spécialité"
            )

        db_service = Service(
            id=str(uuid.uuid4()),
            nom=obj_in.nom,
            speciality_id=obj_in.speciality_id,
            duree_stage_jours=obj_in.duree_stage_jours,
            places_disponibles=obj_in.places_disponibles
        )

        try:
            db.add(db_service)
            db.commit()
            db.refresh(db_service)
            return db_service
        except Exception as e:
            handle_unique_constraint(e, "Le service")

    def update_with_validation(
        self, db: Session, *, db_obj: Service, obj_in: ServiceCreate
    ) -> Service:
        # Validate speciality exists if being changed
        if obj_in.speciality_id != db_obj.speciality_id:
            speciality = db.query(Speciality).filter(
                Speciality.id == obj_in.speciality_id).first()
            if not speciality:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Spécialité non trouvée"
                )

        # Validate name
        validate_string_length(obj_in.nom, "nom du service", 2, 200)

        # Validate duration
        if obj_in.duree_stage_jours < 1 or obj_in.duree_stage_jours > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La durée du stage doit être entre 1 et 365 jours"
            )

        # Validate capacity
        if obj_in.places_disponibles < 1 or obj_in.places_disponibles > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nombre de places doit être entre 1 et 100"
            )

        # Check for duplicate service name (excluding current service)
        existing_service = db.query(Service).filter(
            Service.nom == obj_in.nom,
            Service.speciality_id == obj_in.speciality_id,
            Service.id != db_obj.id
        ).first()

        if existing_service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un service avec ce nom existe déjà dans cette spécialité"
            )

        try:
            for field, value in obj_in.dict(exclude_unset=True).items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            handle_unique_constraint(e, "Le service")


service = CRUDService(Service)
