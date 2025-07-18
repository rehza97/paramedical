from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func, Date
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import uuid
import logging

from .base import CRUDBase
from ..models import Rotation, Etudiant, Service, Planning
from ..schemas import RotationCreate, RotationBase, RotationUpdate
from .utils import validate_string_length, handle_db_commit, handle_unique_constraint, db_commit_context

logger = logging.getLogger(__name__)


class CRUDRotation(CRUDBase[Rotation, RotationCreate, RotationBase]):
    def get_by_planning(self, db: Session, *, planning_id: str) -> List[Rotation]:
        return db.query(Rotation).filter(Rotation.planning_id == planning_id).order_by(Rotation.ordre).all()

    def get_by_student(self, db: Session, *, etudiant_id: str) -> List[Rotation]:
        return db.query(Rotation).filter(Rotation.etudiant_id == etudiant_id).order_by(Rotation.ordre).all()

    def get_by_service(self, db: Session, *, service_id: str) -> List[Rotation]:
        return db.query(Rotation).filter(Rotation.service_id == service_id).order_by(Rotation.ordre).all()

    def create_with_validation(
        self, db: Session, *, obj_in: RotationCreate
    ) -> Rotation:
        # Validate student exists
        etudiant = db.query(Etudiant).filter(
            Etudiant.id == obj_in.etudiant_id).first()
        if not etudiant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Étudiant non trouvé"
            )

        # Validate service exists
        service = db.query(Service).filter(
            Service.id == obj_in.service_id).first()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service non trouvé"
            )

        # Validate planning exists
        planning = db.query(Planning).filter(
            Planning.id == obj_in.planning_id).first()
        if not planning:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planning non trouvé"
            )

        # Validate date format
        try:
            datetime.strptime(obj_in.date_debut, "%Y-%m-%d")
            datetime.strptime(obj_in.date_fin, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )

        # Validate date order
        if obj_in.date_debut >= obj_in.date_fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de début doit être antérieure à la date de fin"
            )

        # Check for overlapping rotations for the same student
        overlapping = db.query(Rotation).filter(
            Rotation.etudiant_id == obj_in.etudiant_id,
            Rotation.id != obj_in.id if hasattr(obj_in, 'id') else True,
            Rotation.date_debut <= obj_in.date_fin,
            Rotation.date_fin >= obj_in.date_debut
        ).first()

        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'étudiant a déjà une rotation sur cette période"
            )

        # Check service capacity
        service_rotations = db.query(Rotation).filter(
            Rotation.service_id == obj_in.service_id,
            Rotation.date_debut <= obj_in.date_fin,
            Rotation.date_fin >= obj_in.date_debut
        ).count()

        if service_rotations >= service.places_disponibles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le service {service.nom} a atteint sa capacité maximale ({service.places_disponibles} places)"
            )

        db_rotation = Rotation(
            id=str(uuid.uuid4()),
            etudiant_id=obj_in.etudiant_id,
            service_id=obj_in.service_id,
            planning_id=obj_in.planning_id,
            date_debut=obj_in.date_debut,
            date_fin=obj_in.date_fin,
            ordre=obj_in.ordre
        )

        try:
            db.add(db_rotation)
            db.commit()
            db.refresh(db_rotation)
            return db_rotation
        except Exception as e:
            handle_unique_constraint(e, "La rotation")

    def update_with_validation(
        self, db: Session, *, db_obj: Rotation, obj_in: RotationCreate
    ) -> Rotation:
        # Validate service exists
        service = db.query(Service).filter(
            Service.id == obj_in.service_id).first()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service non trouvé"
            )

        # Validate date format
        try:
            datetime.strptime(obj_in.date_debut, "%Y-%m-%d")
            datetime.strptime(obj_in.date_fin, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )

        # Validate date order
        if obj_in.date_debut >= obj_in.date_fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de début doit être antérieure à la date de fin"
            )

        # Check for overlapping rotations (excluding current rotation)
        overlapping = db.query(Rotation).filter(
            Rotation.etudiant_id == obj_in.etudiant_id,
            Rotation.id != db_obj.id,
            Rotation.date_debut <= obj_in.date_fin,
            Rotation.date_fin >= obj_in.date_debut
        ).first()

        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'étudiant a déjà une rotation sur cette période"
            )

        # Check service capacity (excluding current rotation)
        service_rotations = db.query(Rotation).filter(
            Rotation.service_id == obj_in.service_id,
            Rotation.id != db_obj.id,
            Rotation.date_debut <= obj_in.date_fin,
            Rotation.date_fin >= obj_in.date_debut
        ).count()

        if service_rotations >= service.places_disponibles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le service {service.nom} a atteint sa capacité maximale ({service.places_disponibles} places)"
            )

        try:
            for field, value in obj_in.dict(exclude_unset=True).items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            handle_unique_constraint(e, "La rotation")

    def get_current_rotation(
        self, db: Session, *, etudiant_id: str, planning_id: str
    ) -> Optional[Rotation]:
        """Get current rotation for a student in a planning"""
        current_date = datetime.now().date()
        return db.query(Rotation).filter(
            Rotation.etudiant_id == etudiant_id,
            Rotation.planning_id == planning_id,
            Rotation.date_debut <= current_date,
            Rotation.date_fin >= current_date
        ).first()

    def get_next_rotation(
        self, db: Session, *, etudiant_id: str, planning_id: str
    ) -> Optional[Rotation]:
        """Get next rotation for a student in a planning"""
        current_date = datetime.now().date()
        return db.query(Rotation).filter(
            Rotation.etudiant_id == etudiant_id,
            Rotation.planning_id == planning_id,
            Rotation.date_debut > current_date
        ).order_by(Rotation.date_debut).first()

    def get_rotations_by_date_range(
        self, db: Session, *, date_debut: datetime, date_fin: datetime
    ) -> List[Rotation]:
        """Get rotations within a date range"""
        return db.query(Rotation).filter(
            Rotation.date_debut <= date_fin,
            Rotation.date_fin >= date_debut
        ).order_by(Rotation.date_debut).all()

    def reorder_rotations(
        self, db: Session, *, etudiant_id: str, planning_id: str, new_orders: List[dict]
    ) -> List[Rotation]:
        """Reorder rotations for a student in a planning"""
        # new_orders should be a list of {'rotation_id': str, 'ordre': int}
        try:
            for order_data in new_orders:
                rotation = db.query(Rotation).filter(
                    Rotation.id == order_data['rotation_id'],
                    Rotation.etudiant_id == etudiant_id,
                    Rotation.planning_id == planning_id
                ).first()

                if rotation:
                    rotation.ordre = order_data['ordre']

            db.commit()

            # Return updated rotations
            return self.get_by_student_and_planning(
                db=db, etudiant_id=etudiant_id, planning_id=planning_id
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la réorganisation: {str(e)}"
            )

    def validate_all_assignments(
        self, db: Session, *, planning_id: str
    ) -> Dict[str, Any]:
        """Validate all rotations in a planning and return validation results"""
        try:
            # Get all rotations for this planning
            rotations = self.get_by_planning(db, planning_id=planning_id)

            errors = []
            warnings = []

            # Check for overlapping rotations per student
            student_rotations = {}
            for rotation in rotations:
                if rotation.etudiant_id not in student_rotations:
                    student_rotations[rotation.etudiant_id] = []
                student_rotations[rotation.etudiant_id].append(rotation)

            # Validate each student's rotations
            for etudiant_id, student_rots in student_rotations.items():
                # Sort by start date
                student_rots.sort(key=lambda x: x.date_debut)

                # Check for overlaps
                for i in range(len(student_rots) - 1):
                    current = student_rots[i]
                    next_rotation = student_rots[i + 1]

                    # Check if there's a gap between rotations
                    current_end = datetime.strptime(
                        current.date_fin, "%Y-%m-%d").date()
                    next_start = datetime.strptime(
                        next_rotation.date_debut, "%Y-%m-%d").date()

                    if next_start > current_end + timedelta(days=1):
                        warnings.append(
                            f"Gap detected for student {current.etudiant.prenom} {current.etudiant.nom}: "
                            f"{current_end} to {next_start}"
                        )

                    # Check for overlaps
                    if current_end >= next_start:
                        errors.append(
                            f"Overlapping rotations for student {current.etudiant.prenom} {current.etudiant.nom}: "
                            f"{current.date_debut} to {current.date_fin} overlaps with "
                            f"{next_rotation.date_debut} to {next_rotation.date_fin}"
                        )

            # Check service capacity violations
            service_rotations = {}
            for rotation in rotations:
                if rotation.service_id not in service_rotations:
                    service_rotations[rotation.service_id] = []
                service_rotations[rotation.service_id].append(rotation)

            for service_id, service_rots in service_rotations.items():
                service = db.query(Service).filter(
                    Service.id == service_id).first()
                if not service:
                    continue

                # Check capacity for each day
                for rotation in service_rots:
                    start_date = datetime.strptime(
                        rotation.date_debut, "%Y-%m-%d").date()
                    end_date = datetime.strptime(
                        rotation.date_fin, "%Y-%m-%d").date()

                    # Count overlapping rotations for this service
                    overlapping_count = db.query(Rotation).filter(
                        Rotation.service_id == service_id,
                        Rotation.date_debut <= rotation.date_fin,
                        Rotation.date_fin >= rotation.date_debut
                    ).count()

                    if overlapping_count > service.places_disponibles:
                        errors.append(
                            f"Service {service.nom} capacity exceeded: "
                            f"{overlapping_count} students assigned, capacity is {service.places_disponibles}"
                        )
                        break

            # Check for students with no rotations
            planning = db.query(Planning).filter(
                Planning.id == planning_id).first()
            if planning and planning.promotion:
                all_students = db.query(Etudiant).filter(
                    Etudiant.promotion_id == planning.promo_id,
                    Etudiant.is_active == True
                ).all()

                students_with_rotations = set(
                    rotation.etudiant_id for rotation in rotations)
                students_without_rotations = [
                    student for student in all_students
                    if student.id not in students_with_rotations
                ]

                if students_without_rotations:
                    warnings.append(
                        f"{len(students_without_rotations)} students have no rotations assigned"
                    )

            is_valid = len(errors) == 0

            return {
                "is_valid": is_valid,
                "erreurs": errors,
                "warnings": warnings,
                "total_rotations": len(rotations),
                "total_students": len(student_rotations),
                "total_services": len(service_rotations)
            }

        except Exception as e:
            logger.error(f"Error validating planning {planning_id}: {str(e)}")
            return {
                "is_valid": False,
                "erreurs": [f"Error during validation: {str(e)}"],
                "warnings": [],
                "total_rotations": 0,
                "total_students": 0,
                "total_services": 0
            }


rotation = CRUDRotation(Rotation)
