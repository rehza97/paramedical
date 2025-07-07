from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from .base import CRUDBase
from ..models import Promotion, Etudiant
from ..schemas import PromotionCreate, PromotionBase
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context


class CRUDPromotion(CRUDBase[Promotion, PromotionCreate, PromotionBase]):
    def create_with_students(
        self, db: Session, *, obj_in: PromotionCreate
    ) -> Promotion:
        if not obj_in.etudiants or len(obj_in.etudiants) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La promotion doit contenir au moins un étudiant."
            )
        validate_string_length(obj_in.nom, "nom de la promotion", 2, 200)
        db_promotion = Promotion(
            id=str(uuid.uuid4()),
            nom=obj_in.nom,
            annee=obj_in.annee,
            speciality_id=obj_in.speciality_id
        )
        db.add(db_promotion)
        db.flush()
        for etudiant_data in obj_in.etudiants:
            db_etudiant = Etudiant(
                id=str(uuid.uuid4()),
                nom=etudiant_data.nom,
                prenom=etudiant_data.prenom,
                promotion_id=db_promotion.id,
                annee_courante=1
            )
            db.add(db_etudiant)
        from .promotion_year import promotion_year
        promotion_year.create_promotion_years_for_promotion(
            db=db, promotion_id=db_promotion.id)
        try:
            db.commit()
            db.refresh(db_promotion)
            return db_promotion
        except Exception as e:
            handle_unique_constraint(e, "Le nom de la promotion")

    def get_with_students(self, db: Session, id: str) -> Optional[Promotion]:
        return db.query(Promotion).filter(Promotion.id == id).first()

    def update_with_students(
        self, db: Session, *, db_obj: Promotion, obj_in: PromotionCreate
    ) -> Promotion:
        """Update a promotion with students"""
        validate_string_length(obj_in.nom, "nom de la promotion", 2, 200)

        # Update basic promotion info
        db_obj.nom = obj_in.nom
        db_obj.annee = obj_in.annee
        db_obj.speciality_id = obj_in.speciality_id

        # Handle students update
        if obj_in.etudiants:
            # Get existing students
            existing_students = db.query(Etudiant).filter(Etudiant.promotion_id == db_obj.id).all()
            
            # Delete related data first to avoid foreign key constraint violations
            for student in existing_students:
                # Delete student schedule details first
                from ..models import Rotation, StudentSchedule, StudentScheduleDetail
                
                # Get student schedules
                student_schedules = db.query(StudentSchedule).filter(StudentSchedule.etudiant_id == student.id).all()
                
                # Delete schedule details
                for schedule in student_schedules:
                    db.query(StudentScheduleDetail).filter(StudentScheduleDetail.schedule_id == schedule.id).delete()
                
                # Delete student schedules
                db.query(StudentSchedule).filter(StudentSchedule.etudiant_id == student.id).delete()
                
                # Delete rotations for this student
                db.query(Rotation).filter(Rotation.etudiant_id == student.id).delete()
            
            # Now safely delete students
            db.query(Etudiant).filter(Etudiant.promotion_id == db_obj.id).delete()
            
            # Add new students
            for etudiant_data in obj_in.etudiants:
                db_etudiant = Etudiant(
                    id=str(uuid.uuid4()),
                    nom=etudiant_data.nom,
                    prenom=etudiant_data.prenom,
                    promotion_id=db_obj.id,
                    annee_courante=1
                )
                db.add(db_etudiant)

        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            handle_unique_constraint(e, "Le nom de la promotion")

    def delete_with_cascade(self, db: Session, *, id: str) -> Promotion:
        promotion = self.get(db=db, id=id)
        if not promotion:
            raise HTTPException(
                status_code=404, detail="Promotion non trouvée")
        from ..models import Planning, Rotation, StudentSchedule, StudentScheduleDetail
        plannings = db.query(Planning).filter(Planning.promo_id == id).all()
        for planning in plannings:
            db.query(StudentScheduleDetail).filter(
                StudentScheduleDetail.schedule_id.in_(
                    db.query(StudentSchedule.id).filter(
                        StudentSchedule.planning_id == planning.id)
                )
            ).delete(synchronize_session=False)
            db.query(StudentSchedule).filter(
                StudentSchedule.planning_id == planning.id).delete()
            db.query(Rotation).filter(
                Rotation.planning_id == planning.id).delete()
        db.query(Planning).filter(Planning.promo_id == id).delete()
        db.delete(promotion)
        try:
            db.commit()
            return promotion
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la suppression de la promotion: {str(e)}"
            )


promotion = CRUDPromotion(Promotion)
