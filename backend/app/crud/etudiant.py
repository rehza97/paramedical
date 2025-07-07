from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import Etudiant, Promotion
from ..schemas import EtudiantCreate, EtudiantBase
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context


class CRUDEtudiant(CRUDBase[Etudiant, EtudiantCreate, EtudiantBase]):
    def get_by_promotion(self, db: Session, *, promotion_id: str) -> List[Etudiant]:
        return db.query(Etudiant).filter(Etudiant.promotion_id == promotion_id).all()

    def create_with_validation(
        self, db: Session, *, obj_in: EtudiantCreate
    ) -> Etudiant:
        # Validate promotion exists
        promotion = db.query(Promotion).filter(
            Promotion.id == obj_in.promotion_id).first()
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion non trouvée"
            )

        # Validate name fields
        validate_string_length(obj_in.nom, "nom", 2, 100)
        validate_string_length(obj_in.prenom, "prénom", 2, 100)

        # Validate year
        if obj_in.annee_courante < 1 or obj_in.annee_courante > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'année courante doit être entre 1 et 10"
            )

        # Check for duplicate student in same promotion
        existing_student = db.query(Etudiant).filter(
            Etudiant.nom == obj_in.nom,
            Etudiant.prenom == obj_in.prenom,
            Etudiant.promotion_id == obj_in.promotion_id
        ).first()

        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un étudiant avec ce nom et prénom existe déjà dans cette promotion"
            )

        db_etudiant = Etudiant(
            id=str(uuid.uuid4()),
            nom=obj_in.nom,
            prenom=obj_in.prenom,
            promotion_id=obj_in.promotion_id,
            annee_courante=obj_in.annee_courante
        )

        try:
            db.add(db_etudiant)
            db.commit()
            db.refresh(db_etudiant)
            return db_etudiant
        except Exception as e:
            handle_unique_constraint(e, "L'étudiant")

    def update_with_validation(
        self, db: Session, *, db_obj: Etudiant, obj_in: EtudiantCreate
    ) -> Etudiant:
        # Validate promotion exists if being changed
        if obj_in.promotion_id != db_obj.promotion_id:
            promotion = db.query(Promotion).filter(
                Promotion.id == obj_in.promotion_id).first()
            if not promotion:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Promotion non trouvée"
                )

        # Validate name fields
        validate_string_length(obj_in.nom, "nom", 2, 100)
        validate_string_length(obj_in.prenom, "prénom", 2, 100)

        # Validate year
        if obj_in.annee_courante < 1 or obj_in.annee_courante > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'année courante doit être entre 1 et 10"
            )

        # Check for duplicate student (excluding current student)
        existing_student = db.query(Etudiant).filter(
            Etudiant.nom == obj_in.nom,
            Etudiant.prenom == obj_in.prenom,
            Etudiant.promotion_id == obj_in.promotion_id,
            Etudiant.id != db_obj.id
        ).first()

        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un étudiant avec ce nom et prénom existe déjà dans cette promotion"
            )

        try:
            for field, value in obj_in.dict(exclude_unset=True).items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            handle_unique_constraint(e, "L'étudiant")

    def get_by_name(self, db: Session, *, nom: str, prenom: str) -> Optional[Etudiant]:
        return db.query(Etudiant).filter(
            Etudiant.nom == nom,
            Etudiant.prenom == prenom
        ).first()

    def get_by_promotion_and_name(
        self, db: Session, *, promotion_id: str, nom: str, prenom: str
    ) -> Optional[Etudiant]:
        return db.query(Etudiant).filter(
            Etudiant.promotion_id == promotion_id,
            Etudiant.nom == nom,
            Etudiant.prenom == prenom
        ).first()


etudiant = CRUDEtudiant(Etudiant)
