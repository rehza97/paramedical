from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
import uuid
from datetime import datetime

from .base import CRUDBase
from ..models import Speciality
from ..schemas import SpecialityCreate, SpecialityBase
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context


class CRUDSpeciality(CRUDBase[Speciality, SpecialityCreate, SpecialityBase]):
    VALID_DURATIONS = [3, 4, 5]

    def _validate_duration(self, duration: int) -> None:
        if duration not in self.VALID_DURATIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"La durée doit être de {', '.join(map(str, self.VALID_DURATIONS))} années."
            )

    def create_with_validation(
        self, db: Session, *, obj_in: SpecialityCreate
    ) -> Speciality:
        validate_string_length(obj_in.nom, "nom de la spécialité", 2, 100)
        self._validate_duration(obj_in.duree_annees)
        existing_specialty = db.query(Speciality).filter(
            Speciality.nom.ilike(obj_in.nom.strip())
        ).first()
        if existing_specialty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Une spécialité avec ce nom existe déjà."
            )
        try:
            db_speciality = Speciality(
                id=str(uuid.uuid4()),
                nom=obj_in.nom.strip(),
                description=obj_in.description.strip() if obj_in.description else None,
                duree_annees=obj_in.duree_annees
            )
            db.add(db_speciality)
            db.commit()
            db.refresh(db_speciality)
            return db_speciality
        except Exception as e:
            handle_unique_constraint(e, "Le nom de la spécialité")

    def update_with_validation(
        self, db: Session, *, db_obj: Speciality, obj_in: SpecialityCreate
    ) -> Speciality:
        validate_string_length(obj_in.nom, "nom de la spécialité", 2, 100)
        self._validate_duration(obj_in.duree_annees)
        existing_specialty = db.query(Speciality).filter(
            Speciality.nom.ilike(obj_in.nom.strip()),
            Speciality.id != db_obj.id
        ).first()
        if existing_specialty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Une autre spécialité avec ce nom existe déjà."
            )
        try:
            db_obj.nom = obj_in.nom.strip()
            db_obj.description = obj_in.description.strip() if obj_in.description else None
            db_obj.duree_annees = obj_in.duree_annees
            db_obj.date_modification = datetime.now()
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            handle_unique_constraint(e, "Le nom de la spécialité")

    def get_by_name(self, db: Session, *, name: str) -> Optional[Speciality]:
        """Get a speciality by name (case-insensitive)"""
        return db.query(Speciality).filter(
            Speciality.nom.ilike(name.strip())
        ).first()

    def get_by_duration(self, db: Session, *, duration: int) -> List[Speciality]:
        """Get all specialities with a specific duration"""
        self._validate_duration(duration)
        return db.query(Speciality).filter(
            Speciality.duree_annees == duration
        ).order_by(Speciality.nom).all()

    def get_all_active(self, db: Session) -> List[Speciality]:
        """Get all active specialities"""
        return db.query(Speciality).filter(
            Speciality.is_active == True
        ).order_by(Speciality.nom).all()

    def search_by_name(self, db: Session, *, search_term: str) -> List[Speciality]:
        """Search specialities by name (partial match)"""
        if not search_term or len(search_term.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Le terme de recherche doit contenir au moins 2 caractères."
            )

        return db.query(Speciality).filter(
            Speciality.nom.ilike(f"%{search_term.strip()}%")
        ).order_by(Speciality.nom).all()

    def deactivate(self, db: Session, *, id: str) -> Speciality:
        """Deactivate a speciality instead of deleting it"""
        db_obj = self.get(db, id=id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spécialité non trouvée."
            )

        try:
            db_obj.is_active = False
            db_obj.date_modification = datetime.now()
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la désactivation: {str(e)}"
            )

    def reactivate(self, db: Session, *, id: str) -> Speciality:
        """Reactivate a speciality"""
        db_obj = self.get(db, id=id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spécialité non trouvée."
            )

        try:
            db_obj.is_active = True
            db_obj.date_modification = datetime.now()
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la réactivation: {str(e)}"
            )

    def get_statistics(self, db: Session) -> dict:
        """Get specialty statistics"""
        try:
            total_specialties = db.query(Speciality).count()
            active_specialties = db.query(Speciality).filter(
                Speciality.is_active == True
            ).count()

            duration_stats = {}
            for duration in self.VALID_DURATIONS:
                count = db.query(Speciality).filter(
                    Speciality.duree_annees == duration,
                    Speciality.is_active == True
                ).count()
                duration_stats[f"duree_{duration}_ans"] = count

            return {
                "total_specialites": total_specialties,
                "specialites_actives": active_specialties,
                "specialites_inactives": total_specialties - active_specialties,
                "repartition_par_duree": duration_stats
            }

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors du calcul des statistiques: {str(e)}"
            )

    def remove(self, db: Session, *, id: str) -> Speciality:
        """Remove a speciality with proper foreign key constraint handling"""
        from ..models import Service, Promotion  # Import here to avoid circular imports

        db_obj = self.get(db, id=id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spécialité non trouvée."
            )

        # Check if there are services referencing this speciality
        services_count = db.query(Service).filter(
            Service.speciality_id == id).count()
        if services_count > 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Impossible de supprimer cette spécialité car elle est référencée par {services_count} service(s). Veuillez d'abord supprimer ou modifier ces services."
            )

        # Check if there are promotions referencing this speciality
        promotions_count = db.query(Promotion).filter(
            Promotion.speciality_id == id).count()
        if promotions_count > 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Impossible de supprimer cette spécialité car elle est référencée par {promotions_count} promotion(s). Veuillez d'abord supprimer ou modifier ces promotions."
            )

        try:
            db.delete(db_obj)
            db.commit()
            return db_obj

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la suppression: {str(e)}"
            )


# Create instance
speciality = CRUDSpeciality(Speciality)
