from typing import List, Optional
from sqlalchemy.orm import Session

from .base import CRUDBase
from ..models import Etudiant
from ..schemas import EtudiantCreate, EtudiantBase

class CRUDEtudiant(CRUDBase[Etudiant, EtudiantCreate, EtudiantBase]):
    def get_by_promotion(self, db: Session, *, promotion_id: str) -> List[Etudiant]:
        """Get all students in a promotion"""
        return db.query(Etudiant).filter(Etudiant.promotion_id == promotion_id).all()

    def get_by_name(self, db: Session, *, nom: str, prenom: str) -> Optional[Etudiant]:
        """Get student by full name"""
        return db.query(Etudiant).filter(
            Etudiant.nom == nom, 
            Etudiant.prenom == prenom
        ).first()

etudiant = CRUDEtudiant(Etudiant) 
from sqlalchemy.orm import Session

from .base import CRUDBase
from ..models import Etudiant
from ..schemas import EtudiantCreate, EtudiantBase

class CRUDEtudiant(CRUDBase[Etudiant, EtudiantCreate, EtudiantBase]):
    def get_by_promotion(self, db: Session, *, promotion_id: str) -> List[Etudiant]:
        """Get all students in a promotion"""
        return db.query(Etudiant).filter(Etudiant.promotion_id == promotion_id).all()

    def get_by_name(self, db: Session, *, nom: str, prenom: str) -> Optional[Etudiant]:
        """Get student by full name"""
        return db.query(Etudiant).filter(
            Etudiant.nom == nom, 
            Etudiant.prenom == prenom
        ).first()

etudiant = CRUDEtudiant(Etudiant) 
 
 