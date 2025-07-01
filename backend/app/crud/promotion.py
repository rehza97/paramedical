from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import Promotion, Etudiant
from ..schemas import PromotionCreate, PromotionBase

class CRUDPromotion(CRUDBase[Promotion, PromotionCreate, PromotionBase]):
    def create_with_students(
        self, db: Session, *, obj_in: PromotionCreate
    ) -> Promotion:
        """Create a promotion with students"""
        # Validation: must have at least one student
        if not obj_in.etudiants or len(obj_in.etudiants) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="La promotion doit contenir au moins un étudiant."
            )
        
        # Create promotion
        db_promotion = Promotion(
            id=str(uuid.uuid4()),
            nom=obj_in.nom,
            annee=obj_in.annee,
            speciality_id=obj_in.speciality_id
        )
        db.add(db_promotion)
        db.flush()  # Get the promotion ID
        
        # Create students
        for etudiant_data in obj_in.etudiants:
            db_etudiant = Etudiant(
                id=str(uuid.uuid4()),
                nom=etudiant_data.nom,
                prenom=etudiant_data.prenom,
                promotion_id=db_promotion.id,
                annee_courante=1  # Start in first year
            )
            db.add(db_etudiant)
        
        db.commit()
        
        # Create promotion years based on speciality duration
        from .promotion_year import promotion_year
        promotion_year.create_promotion_years_for_promotion(db=db, promotion_id=db_promotion.id)
        
        db.refresh(db_promotion)
        return db_promotion

    def get_with_students(self, db: Session, id: str) -> Optional[Promotion]:
        """Get promotion with all students loaded"""
        return db.query(Promotion).filter(Promotion.id == id).first()

    def delete_with_cascade(self, db: Session, *, id: str) -> Promotion:
        """Delete promotion and all associated data"""
        promotion = self.get(db=db, id=id)
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion non trouvée")
        
        # Delete in correct order to avoid foreign key violations
        from ..models import Planning, Rotation, StudentSchedule, StudentScheduleDetail
        
        # First, delete all student schedule details
        plannings = db.query(Planning).filter(Planning.promo_id == id).all()
        for planning in plannings:
            # Delete student schedule details
            db.query(StudentScheduleDetail).filter(
                StudentScheduleDetail.schedule_id.in_(
                    db.query(StudentSchedule.id).filter(StudentSchedule.planning_id == planning.id)
                )
            ).delete(synchronize_session=False)
            
            # Delete student schedules
            db.query(StudentSchedule).filter(StudentSchedule.planning_id == planning.id).delete()
            
            # Delete rotations
            db.query(Rotation).filter(Rotation.planning_id == planning.id).delete()
        
        # Delete plannings
        db.query(Planning).filter(Planning.promo_id == id).delete()
        
        # Delete promotion (cascade will handle students)
        db.delete(promotion)
        db.commit()
        return promotion

promotion = CRUDPromotion(Promotion) 
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import Promotion, Etudiant
from ..schemas import PromotionCreate, PromotionBase

class CRUDPromotion(CRUDBase[Promotion, PromotionCreate, PromotionBase]):
    def create_with_students(
        self, db: Session, *, obj_in: PromotionCreate
    ) -> Promotion:
        """Create a promotion with students"""
        # Validation: must have at least one student
        if not obj_in.etudiants or len(obj_in.etudiants) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="La promotion doit contenir au moins un étudiant."
            )
        
        # Create promotion
        db_promotion = Promotion(
            id=str(uuid.uuid4()),
            nom=obj_in.nom,
            annee=obj_in.annee,
            speciality_id=obj_in.speciality_id
        )
        db.add(db_promotion)
        db.flush()  # Get the promotion ID
        
        # Create students
        for etudiant_data in obj_in.etudiants:
            db_etudiant = Etudiant(
                id=str(uuid.uuid4()),
                nom=etudiant_data.nom,
                prenom=etudiant_data.prenom,
                promotion_id=db_promotion.id,
                annee_courante=1  # Start in first year
            )
            db.add(db_etudiant)
        
        db.commit()
        
        # Create promotion years based on speciality duration
        from .promotion_year import promotion_year
        promotion_year.create_promotion_years_for_promotion(db=db, promotion_id=db_promotion.id)
        
        db.refresh(db_promotion)
        return db_promotion

    def get_with_students(self, db: Session, id: str) -> Optional[Promotion]:
        """Get promotion with all students loaded"""
        return db.query(Promotion).filter(Promotion.id == id).first()

    def delete_with_cascade(self, db: Session, *, id: str) -> Promotion:
        """Delete promotion and all associated data"""
        promotion = self.get(db=db, id=id)
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion non trouvée")
        
        # Delete in correct order to avoid foreign key violations
        from ..models import Planning, Rotation, StudentSchedule, StudentScheduleDetail
        
        # First, delete all student schedule details
        plannings = db.query(Planning).filter(Planning.promo_id == id).all()
        for planning in plannings:
            # Delete student schedule details
            db.query(StudentScheduleDetail).filter(
                StudentScheduleDetail.schedule_id.in_(
                    db.query(StudentSchedule.id).filter(StudentSchedule.planning_id == planning.id)
                )
            ).delete(synchronize_session=False)
            
            # Delete student schedules
            db.query(StudentSchedule).filter(StudentSchedule.planning_id == planning.id).delete()
            
            # Delete rotations
            db.query(Rotation).filter(Rotation.planning_id == planning.id).delete()
        
        # Delete plannings
        db.query(Planning).filter(Planning.promo_id == id).delete()
        
        # Delete promotion (cascade will handle students)
        db.delete(promotion)
        db.commit()
        return promotion

promotion = CRUDPromotion(Promotion) 
 
 