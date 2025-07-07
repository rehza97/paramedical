from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import PromotionYear, Promotion, Speciality
from ..schemas import PromotionYearCreate, PromotionYearBase
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context


class CRUDPromotionYear(CRUDBase[PromotionYear, PromotionYearCreate, PromotionYearBase]):
    def get_by_promotion(self, db: Session, *, promotion_id: str) -> List[PromotionYear]:
        return db.query(PromotionYear).filter(PromotionYear.promotion_id == promotion_id).order_by(PromotionYear.annee_niveau).all()

    def get_by_promotion_id(self, db: Session, *, promotion_id: str) -> List[PromotionYear]:
        """Alias for get_by_promotion to match endpoint expectations"""
        return self.get_by_promotion(db=db, promotion_id=promotion_id)

    def get_active_year(self, db: Session, *, promotion_id: str) -> Optional[PromotionYear]:
        """Get the active promotion year for a promotion"""
        return db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_id,
            PromotionYear.is_active == True
        ).first()

    def activate_year(self, db: Session, *, year_id: str) -> PromotionYear:
        """Activate a promotion year and deactivate others in the same promotion"""
        year = self.get(db=db, id=year_id)
        if not year:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Année de promotion non trouvée"
            )

        # Deactivate all years in the same promotion
        db.query(PromotionYear).filter(
            PromotionYear.promotion_id == year.promotion_id
        ).update({"is_active": False})

        # Activate the selected year
        year.is_active = True

        try:
            db.commit()
            db.refresh(year)
            return year
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de l'activation: {str(e)}"
            )

    def create_promotion_years_for_promotion(
        self, db: Session, *, promotion_id: str
    ) -> List[PromotionYear]:
        # Get promotion and its speciality
        promotion = db.query(Promotion).filter(
            Promotion.id == promotion_id).first()
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion non trouvée"
            )

        speciality = db.query(Speciality).filter(
            Speciality.id == promotion.speciality_id).first()
        if not speciality:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spécialité non trouvée"
            )

        # Delete existing promotion years for this promotion
        db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_id).delete()

        # Create promotion years based on speciality duration
        promotion_years = []
        for annee in range(1, speciality.duree_annees + 1):
            # Calculate calendar year (promotion start year + current year level - 1)
            annee_calendaire = promotion.annee + annee - 1

            db_promotion_year = PromotionYear(
                id=str(uuid.uuid4()),
                promotion_id=promotion_id,
                annee_niveau=annee,
                annee_calendaire=annee_calendaire,
                nom=f"Année {annee}"
            )
            promotion_years.append(db_promotion_year)
            db.add(db_promotion_year)

        try:
            db.commit()
            return promotion_years
        except Exception as e:
            handle_unique_constraint(e, "Les années de promotion")

    def get_by_promotion_and_year(
        self, db: Session, *, promotion_id: str, annee_niveau: int
    ) -> Optional[PromotionYear]:
        return db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_id,
            PromotionYear.annee_niveau == annee_niveau
        ).first()

    def create_with_validation(
        self, db: Session, *, obj_in: PromotionYearCreate
    ) -> PromotionYear:
        # Validate promotion exists
        promotion = db.query(Promotion).filter(
            Promotion.id == obj_in.promotion_id).first()
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion non trouvée"
            )

        # Validate year level
        if obj_in.annee_niveau < 1 or obj_in.annee_niveau > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'année niveau doit être entre 1 et 10"
            )

        # Validate name
        if obj_in.nom:
            validate_string_length(obj_in.nom, "nom de l'année", 2, 100)

        # Check for duplicate year in same promotion
        existing_year = db.query(PromotionYear).filter(
            PromotionYear.promotion_id == obj_in.promotion_id,
            PromotionYear.annee_niveau == obj_in.annee_niveau
        ).first()

        if existing_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une année avec ce numéro existe déjà dans cette promotion"
            )

        db_promotion_year = PromotionYear(
            id=str(uuid.uuid4()),
            promotion_id=obj_in.promotion_id,
            annee_niveau=obj_in.annee_niveau,
            annee_calendaire=obj_in.annee_calendaire,
            nom=obj_in.nom
        )

        try:
            db.add(db_promotion_year)
            db.commit()
            db.refresh(db_promotion_year)
            return db_promotion_year
        except Exception as e:
            handle_unique_constraint(e, "L'année de promotion")


promotion_year = CRUDPromotionYear(PromotionYear)
