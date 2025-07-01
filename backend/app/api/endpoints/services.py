from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud import service
from ...schemas import Service, ServiceCreate, IdResponse, MessageResponse

router = APIRouter()

@router.post("/", response_model=IdResponse)
def create_service(
    service_in: ServiceCreate, 
    db: Session = Depends(get_db)
):
    """Create a new service"""
    db_service = service.create_with_validation(db=db, obj_in=service_in)
    return {"id": db_service.id, "message": "Service créé avec succès"}

@router.get("/", response_model=List[Service])
def read_services(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all services"""
    services = service.get_multi(db, skip=skip, limit=limit)
    return services

@router.get("/{service_id}", response_model=Service)
def read_service(
    service_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific service by ID"""
    db_service = service.get(db, id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    return db_service

@router.put("/{service_id}", response_model=MessageResponse)
def update_service(
    service_id: str,
    service_in: ServiceCreate,
    db: Session = Depends(get_db)
):
    """Update a service"""
    db_service = service.get(db, id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    service.update_with_validation(db=db, db_obj=db_service, obj_in=service_in)
    return {"message": "Service mis à jour avec succès"}

@router.delete("/{service_id}", response_model=MessageResponse)
def delete_service(
    service_id: str,
    db: Session = Depends(get_db)
):
    """Delete a service"""
    db_service = service.get(db, id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    service.delete_with_cascade(db=db, id=service_id)
    return {"message": "Service supprimé avec succès"} 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud import service
from ...schemas import Service, ServiceCreate, IdResponse, MessageResponse

router = APIRouter()

@router.post("/", response_model=IdResponse)
def create_service(
    service_in: ServiceCreate, 
    db: Session = Depends(get_db)
):
    """Create a new service"""
    db_service = service.create_with_validation(db=db, obj_in=service_in)
    return {"id": db_service.id, "message": "Service créé avec succès"}

@router.get("/", response_model=List[Service])
def read_services(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all services"""
    services = service.get_multi(db, skip=skip, limit=limit)
    return services

@router.get("/{service_id}", response_model=Service)
def read_service(
    service_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific service by ID"""
    db_service = service.get(db, id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    return db_service

@router.put("/{service_id}", response_model=MessageResponse)
def update_service(
    service_id: str,
    service_in: ServiceCreate,
    db: Session = Depends(get_db)
):
    """Update a service"""
    db_service = service.get(db, id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    service.update_with_validation(db=db, db_obj=db_service, obj_in=service_in)
    return {"message": "Service mis à jour avec succès"}

@router.delete("/{service_id}", response_model=MessageResponse)
def delete_service(
    service_id: str,
    db: Session = Depends(get_db)
):
    """Delete a service"""
    db_service = service.get(db, id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    service.delete_with_cascade(db=db, id=service_id)
    return {"message": "Service supprimé avec succès"} 
 
 