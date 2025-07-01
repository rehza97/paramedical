from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import PromotionYear, Promotion, Speciality
from ..schemas import PromotionYearCreate, PromotionYearBase

class CRUDPromotionYear(CRUDBase[PromotionYear, PromotionYearCreate, PromotionYearBase]):
    def create_promotion_years_for_promotion(
        self, db: Session, *, promotion_id: str
    ) -> List[PromotionYear]:
        """Create all years for a promotion based on its speciality duration"""
        # Get the promotion with its speciality
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion non trouvée")
        
        # Get duration from speciality or default to 3 years
        duration = 3  # default
        if promotion.speciality:
            duration = promotion.speciality.duree_annees
        
        promotion_years = []
        for year_level in range(1, duration + 1):
            calendar_year = promotion.annee + (year_level - 1)
            
            promotion_year = PromotionYear(
                id=str(uuid.uuid4()),
                promotion_id=promotion_id,
                annee_niveau=year_level,
                annee_calendaire=calendar_year,
                nom=f"{year_level}{'ère' if year_level == 1 else 'ème'} année",
                is_active=(year_level == 1)  # Only first year is active initially
            )
            db.add(promotion_year)
            promotion_years.append(promotion_year)
        
        db.commit()
        return promotion_years
    
    def get_by_promotion_id(self, db: Session, *, promotion_id: str) -> List[PromotionYear]:
        """Get all years for a specific promotion"""
        return db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_id
        ).order_by(PromotionYear.annee_niveau).all()
    
    def get_active_year(self, db: Session, *, promotion_id: str) -> Optional[PromotionYear]:
        """Get the currently active year for a promotion"""
        return db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_id,
            PromotionYear.is_active == True
        ).first()
    
    def activate_year(self, db: Session, *, promotion_year_id: str) -> PromotionYear:
        """Activate a specific year and deactivate others in the same promotion"""
        promotion_year = self.get(db=db, id=promotion_year_id)
        if not promotion_year:
            raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
        
        # Deactivate all years in the same promotion
        db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_year.promotion_id
        ).update({"is_active": False})
        
        # Activate the selected year
        promotion_year.is_active = True
        db.commit()
        db.refresh(promotion_year)
        
        return promotion_year
    
    def get_by_year_level(self, db: Session, *, promotion_id: str, year_level: int) -> Optional[PromotionYear]:
        """Get a specific year level for a promotion"""
        return db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_id,
            PromotionYear.annee_niveau == year_level
        ).first()

promotion_year = CRUDPromotionYear(PromotionYear) 
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import PromotionYear, Promotion, Speciality
from ..schemas import PromotionYearCreate, PromotionYearBase

class CRUDPromotionYear(CRUDBase[PromotionYear, PromotionYearCreate, PromotionYearBase]):
    def create_promotion_years_for_promotion(
        self, db: Session, *, promotion_id: str
    ) -> List[PromotionYear]:
        """Create all years for a promotion based on its speciality duration"""
        # Get the promotion with its speciality
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion non trouvée")
        
        # Get duration from speciality or default to 3 years
        duration = 3  # default
        if promotion.speciality:
            duration = promotion.speciality.duree_annees
        
        promotion_years = []
        for year_level in range(1, duration + 1):
            calendar_year = promotion.annee + (year_level - 1)
            
            promotion_year = PromotionYear(
                id=str(uuid.uuid4()),
                promotion_id=promotion_id,
                annee_niveau=year_level,
                annee_calendaire=calendar_year,
                nom=f"{year_level}{'ère' if year_level == 1 else 'ème'} année",
                is_active=(year_level == 1)  # Only first year is active initially
            )
            db.add(promotion_year)
            promotion_years.append(promotion_year)
        
        db.commit()
        return promotion_years
    
    def get_by_promotion_id(self, db: Session, *, promotion_id: str) -> List[PromotionYear]:
        """Get all years for a specific promotion"""
        return db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_id
        ).order_by(PromotionYear.annee_niveau).all()
    
    def get_active_year(self, db: Session, *, promotion_id: str) -> Optional[PromotionYear]:
        """Get the currently active year for a promotion"""
        return db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_id,
            PromotionYear.is_active == True
        ).first()
    
    def activate_year(self, db: Session, *, promotion_year_id: str) -> PromotionYear:
        """Activate a specific year and deactivate others in the same promotion"""
        promotion_year = self.get(db=db, id=promotion_year_id)
        if not promotion_year:
            raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
        
        # Deactivate all years in the same promotion
        db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_year.promotion_id
        ).update({"is_active": False})
        
        # Activate the selected year
        promotion_year.is_active = True
        db.commit()
        db.refresh(promotion_year)
        
        return promotion_year
    
    def get_by_year_level(self, db: Session, *, promotion_id: str, year_level: int) -> Optional[PromotionYear]:
        """Get a specific year level for a promotion"""
        return db.query(PromotionYear).filter(
            PromotionYear.promotion_id == promotion_id,
            PromotionYear.annee_niveau == year_level
        ).first()

promotion_year = CRUDPromotionYear(PromotionYear) 
 
 