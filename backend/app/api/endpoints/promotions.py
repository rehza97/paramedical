from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud import promotion, service
from ...schemas import Promotion, PromotionCreate, IdResponse, MessageResponse, Service
from ...models import Etudiant

router = APIRouter()


@router.post("/", response_model=IdResponse)
def create_promotion(
    promotion_in: PromotionCreate,
    db: Session = Depends(get_db)
):
    """Create a new promotion with students"""
    db_promotion = promotion.create_with_students(db=db, obj_in=promotion_in)
    return {"id": db_promotion.id, "message": "Promotion créée avec succès"}


@router.get("/", response_model=List[Promotion])
def read_promotions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all promotions"""
    promotions = promotion.get_multi(db, skip=skip, limit=limit)
    return promotions


@router.get("/{promotion_id}", response_model=Promotion)
def read_promotion(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific promotion by ID"""
    db_promotion = promotion.get_with_students(db, id=promotion_id)
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")
    return db_promotion


@router.put("/{promotion_id}", response_model=MessageResponse)
def update_promotion(
    promotion_id: str,
    promotion_in: PromotionCreate,
    db: Session = Depends(get_db)
):
    """Update a promotion"""
    db_promotion = promotion.get(db, id=promotion_id)
    if not db_promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    updated_promotion = promotion.update_with_students(
        db=db, db_obj=db_promotion, obj_in=promotion_in
    )
    return {"message": "Promotion mise à jour avec succès"}


@router.delete("/{promotion_id}", response_model=MessageResponse)
def delete_promotion(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Delete a promotion and all associated data"""
    promotion.remove(db=db, id=promotion_id)
    return {"message": "Promotion supprimée avec succès"}


# Student management endpoints
@router.put("/{promotion_id}/students/{student_id}/toggle-status", response_model=MessageResponse)
def toggle_student_status(
    promotion_id: str,
    student_id: str,
    db: Session = Depends(get_db)
):
    """Toggle student active status (enable/disable for planning)"""
    # Check if promotion exists
    db_promotion = promotion.get(db, id=promotion_id)
    if not db_promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    # Check if student exists and belongs to this promotion
    db_student = db.query(Etudiant).filter(
        Etudiant.id == student_id,
        Etudiant.promotion_id == promotion_id
    ).first()
    if not db_student:
        raise HTTPException(
            status_code=404, detail="Étudiant non trouvé dans cette promotion")

    # Toggle the status
    db_student.is_active = not db_student.is_active
    db.commit()

    status_text = "activé" if db_student.is_active else "désactivé"
    return {"message": f"Étudiant {db_student.prenom} {db_student.nom} {status_text} avec succès"}


# Promotion-Service assignment endpoints


@router.post("/{promotion_id}/services/{service_id}", response_model=MessageResponse)
def assign_service_to_promotion(
    promotion_id: str,
    service_id: str,
    db: Session = Depends(get_db)
):
    """Assign a service to a promotion"""
    # Check if promotion exists
    db_promotion = promotion.get(db, id=promotion_id)
    if not db_promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    # Check if service exists
    db_service = service.get(db, id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service non trouvé")

    # Check if already assigned
    if db_service in db_promotion.services:
        raise HTTPException(
            status_code=400, detail="Service déjà assigné à cette promotion")

    # Assign service to promotion
    db_promotion.services.append(db_service)
    db.commit()

    return {"message": "Service assigné à la promotion avec succès"}


@router.delete("/{promotion_id}/services/{service_id}", response_model=MessageResponse)
def remove_service_from_promotion(
    promotion_id: str,
    service_id: str,
    db: Session = Depends(get_db)
):
    """Remove a service from a promotion"""
    # Check if promotion exists
    db_promotion = promotion.get(db, id=promotion_id)
    if not db_promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    # Check if service exists
    db_service = service.get(db, id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service non trouvé")

    # Check if service is assigned
    if db_service not in db_promotion.services:
        raise HTTPException(
            status_code=400, detail="Service non assigné à cette promotion")

    # Remove service from promotion
    db_promotion.services.remove(db_service)
    db.commit()

    return {"message": "Service retiré de la promotion avec succès"}


@router.get("/{promotion_id}/services", response_model=List[Service])
def get_promotion_services(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Get all services assigned to a promotion"""
    db_promotion = promotion.get(db, id=promotion_id)
    if not db_promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    return db_promotion.services
