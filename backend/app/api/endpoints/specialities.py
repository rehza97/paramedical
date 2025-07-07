from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud.speciality import speciality
from ...schemas import Speciality, SpecialityCreate, SpecialityBase, IdResponse, MessageResponse

router = APIRouter()


@router.post("/", response_model=IdResponse)
def create_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_in: SpecialityCreate
):
    """Create a new speciality"""
    db_speciality = speciality.create_with_validation(
        db=db, obj_in=speciality_in)
    return {"id": db_speciality.id, "message": "Spécialité créée avec succès"}


@router.get("/", response_model=List[Speciality])
def read_specialities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve all specialities"""
    specialities = speciality.get_multi(db, skip=skip, limit=limit)
    return specialities


@router.get("/{speciality_id}", response_model=Speciality)
def read_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_id: str
):
    """Get a specific speciality by ID"""
    db_speciality = speciality.get(db=db, id=speciality_id)
    if not db_speciality:
        raise HTTPException(status_code=404, detail="Spécialité non trouvée")
    return db_speciality


@router.put("/{speciality_id}", response_model=MessageResponse)
def update_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_id: str,
    speciality_in: SpecialityCreate
):
    """Update a speciality"""
    db_speciality = speciality.get(db=db, id=speciality_id)
    if not db_speciality:
        raise HTTPException(status_code=404, detail="Spécialité non trouvée")

    speciality.update_with_validation(
        db=db, db_obj=db_speciality, obj_in=speciality_in)
    return {"message": "Spécialité mise à jour avec succès"}


@router.delete("/{speciality_id}", response_model=MessageResponse)
def delete_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_id: str
):
    """Delete a speciality"""
    speciality.remove(db=db, id=speciality_id)
    return {"message": "Spécialité supprimée avec succès"}
