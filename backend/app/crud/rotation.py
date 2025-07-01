from typing import List, Optional
from sqlalchemy.orm import Session

from .base import CRUDBase
from ..models import Rotation
from ..schemas import RotationCreate, RotationBase

class CRUDRotation(CRUDBase[Rotation, RotationCreate, RotationBase]):
    def get_by_planning(self, db: Session, *, planning_id: str) -> List[Rotation]:
        """Get all rotations in a planning"""
        return db.query(Rotation).filter(Rotation.planning_id == planning_id).all()

    def get_by_student(self, db: Session, *, etudiant_id: str) -> List[Rotation]:
        """Get all rotations for a student"""
        return db.query(Rotation).filter(Rotation.etudiant_id == etudiant_id).order_by(Rotation.ordre).all()

    def get_by_service(self, db: Session, *, service_id: str) -> List[Rotation]:
        """Get all rotations for a service"""
        return db.query(Rotation).filter(Rotation.service_id == service_id).all()

    def get_by_student_and_planning(
        self, db: Session, *, etudiant_id: str, planning_id: str
    ) -> List[Rotation]:
        """Get all rotations for a student in a specific planning"""
        return db.query(Rotation).filter(
            Rotation.etudiant_id == etudiant_id,
            Rotation.planning_id == planning_id
        ).order_by(Rotation.ordre).all()

rotation = CRUDRotation(Rotation) 
from sqlalchemy.orm import Session

from .base import CRUDBase
from ..models import Rotation
from ..schemas import RotationCreate, RotationBase

class CRUDRotation(CRUDBase[Rotation, RotationCreate, RotationBase]):
    def get_by_planning(self, db: Session, *, planning_id: str) -> List[Rotation]:
        """Get all rotations in a planning"""
        return db.query(Rotation).filter(Rotation.planning_id == planning_id).all()

    def get_by_student(self, db: Session, *, etudiant_id: str) -> List[Rotation]:
        """Get all rotations for a student"""
        return db.query(Rotation).filter(Rotation.etudiant_id == etudiant_id).order_by(Rotation.ordre).all()

    def get_by_service(self, db: Session, *, service_id: str) -> List[Rotation]:
        """Get all rotations for a service"""
        return db.query(Rotation).filter(Rotation.service_id == service_id).all()

    def get_by_student_and_planning(
        self, db: Session, *, etudiant_id: str, planning_id: str
    ) -> List[Rotation]:
        """Get all rotations for a student in a specific planning"""
        return db.query(Rotation).filter(
            Rotation.etudiant_id == etudiant_id,
            Rotation.planning_id == planning_id
        ).order_by(Rotation.ordre).all()

rotation = CRUDRotation(Rotation) 
 
 