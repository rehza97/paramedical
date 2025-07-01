from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud.speciality import speciality
from ...schemas import Speciality, SpecialityCreate, SpecialityBase

router = APIRouter()

@router.post("/", response_model=Speciality)
def create_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_in: SpecialityCreate
):
    """Create a new speciality"""
    return speciality.create(db=db, obj_in=speciality_in)

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
        raise HTTPException(status_code=404, detail="Speciality not found")
    return db_speciality

@router.put("/{speciality_id}", response_model=Speciality)
def update_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_id: str,
    speciality_in: SpecialityCreate
):
    """Update a speciality"""
    db_speciality = speciality.get(db=db, id=speciality_id)
    if not db_speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")
    return speciality.update(db=db, db_obj=db_speciality, obj_in=speciality_in)

@router.delete("/{speciality_id}", response_model=Speciality)
def delete_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_id: str
):
    """Delete a speciality"""
    db_speciality = speciality.get(db=db, id=speciality_id)
    if not db_speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")
    return speciality.remove(db=db, id=speciality_id) 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud.speciality import speciality
from ...schemas import Speciality, SpecialityCreate, SpecialityBase

router = APIRouter()

@router.post("/", response_model=Speciality)
def create_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_in: SpecialityCreate
):
    """Create a new speciality"""
    return speciality.create(db=db, obj_in=speciality_in)

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
        raise HTTPException(status_code=404, detail="Speciality not found")
    return db_speciality

@router.put("/{speciality_id}", response_model=Speciality)
def update_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_id: str,
    speciality_in: SpecialityCreate
):
    """Update a speciality"""
    db_speciality = speciality.get(db=db, id=speciality_id)
    if not db_speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")
    return speciality.update(db=db, db_obj=db_speciality, obj_in=speciality_in)

@router.delete("/{speciality_id}", response_model=Speciality)
def delete_speciality(
    *,
    db: Session = Depends(get_db),
    speciality_id: str
):
    """Delete a speciality"""
    db_speciality = speciality.get(db=db, id=speciality_id)
    if not db_speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")
    return speciality.remove(db=db, id=speciality_id) 
 
 