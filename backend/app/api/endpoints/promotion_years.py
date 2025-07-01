from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud.promotion_year import promotion_year
from ...schemas import PromotionYear, PromotionYearCreate, MessageResponse, Service

router = APIRouter()

@router.post("/create-for-promotion/{promotion_id}", response_model=List[PromotionYear])
def create_promotion_years(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Create all years for a promotion based on its speciality duration"""
    return promotion_year.create_promotion_years_for_promotion(db=db, promotion_id=promotion_id)

@router.get("/promotion/{promotion_id}", response_model=List[PromotionYear])
def get_promotion_years(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Get all years for a specific promotion"""
    return promotion_year.get_by_promotion_id(db=db, promotion_id=promotion_id)

@router.get("/promotion/{promotion_id}/active", response_model=PromotionYear)
def get_active_promotion_year(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Get the currently active year for a promotion"""
    active_year = promotion_year.get_active_year(db=db, promotion_id=promotion_id)
    if not active_year:
        raise HTTPException(status_code=404, detail="Aucune année active trouvée")
    return active_year

@router.put("/{promotion_year_id}/activate", response_model=PromotionYear)
def activate_promotion_year(
    promotion_year_id: str,
    db: Session = Depends(get_db)
):
    """Activate a specific year and deactivate others in the same promotion"""
    return promotion_year.activate_year(db=db, promotion_year_id=promotion_year_id)

@router.get("/{promotion_year_id}", response_model=PromotionYear)
def get_promotion_year(
    promotion_year_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific promotion year by ID"""
    promo_year = promotion_year.get(db=db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    return promo_year

@router.put("/{promotion_year_id}", response_model=PromotionYear)
def update_promotion_year(
    promotion_year_id: str,
    promotion_year_in: PromotionYearCreate,
    db: Session = Depends(get_db)
):
    """Update a promotion year"""
    promo_year = promotion_year.get(db=db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    return promotion_year.update(db=db, db_obj=promo_year, obj_in=promotion_year_in)

# PromotionYear-Service assignment endpoints
@router.post("/{promotion_year_id}/services/{service_id}", response_model=MessageResponse)
def assign_service_to_promotion_year(
    promotion_year_id: str,
    service_id: str,
    db: Session = Depends(get_db)
):
    """Assign a service to a specific year of a promotion"""
    from ...crud.service import service
    
    # Check if promotion year exists
    promo_year = promotion_year.get(db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    
    # Check if service exists
    db_service = service.get(db, id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    # Check if already assigned
    if db_service in promo_year.services:
        raise HTTPException(status_code=400, detail="Service déjà assigné à cette année")
    
    # Assign service to promotion year
    promo_year.services.append(db_service)
    db.commit()
    
    return {"message": "Service assigné à l'année de promotion avec succès"}

@router.delete("/{promotion_year_id}/services/{service_id}", response_model=MessageResponse)
def remove_service_from_promotion_year(
    promotion_year_id: str,
    service_id: str,
    db: Session = Depends(get_db)
):
    """Remove a service from a specific year of a promotion"""
    from ...crud.service import service
    
    # Check if promotion year exists
    promo_year = promotion_year.get(db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    
    # Check if service exists
    db_service = service.get(db, id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    # Check if service is assigned
    if db_service not in promo_year.services:
        raise HTTPException(status_code=400, detail="Service non assigné à cette année")
    
    # Remove service from promotion year
    promo_year.services.remove(db_service)
    db.commit()
    
    return {"message": "Service retiré de l'année de promotion avec succès"}

@router.get("/{promotion_year_id}/services", response_model=List[Service])
def get_promotion_year_services(
    promotion_year_id: str,
    db: Session = Depends(get_db)
):
    """Get all services assigned to a specific year of a promotion"""
    promo_year = promotion_year.get(db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    
    return promo_year.services 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud.promotion_year import promotion_year
from ...schemas import PromotionYear, PromotionYearCreate, MessageResponse, Service

router = APIRouter()

@router.post("/create-for-promotion/{promotion_id}", response_model=List[PromotionYear])
def create_promotion_years(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Create all years for a promotion based on its speciality duration"""
    return promotion_year.create_promotion_years_for_promotion(db=db, promotion_id=promotion_id)

@router.get("/promotion/{promotion_id}", response_model=List[PromotionYear])
def get_promotion_years(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Get all years for a specific promotion"""
    return promotion_year.get_by_promotion_id(db=db, promotion_id=promotion_id)

@router.get("/promotion/{promotion_id}/active", response_model=PromotionYear)
def get_active_promotion_year(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Get the currently active year for a promotion"""
    active_year = promotion_year.get_active_year(db=db, promotion_id=promotion_id)
    if not active_year:
        raise HTTPException(status_code=404, detail="Aucune année active trouvée")
    return active_year

@router.put("/{promotion_year_id}/activate", response_model=PromotionYear)
def activate_promotion_year(
    promotion_year_id: str,
    db: Session = Depends(get_db)
):
    """Activate a specific year and deactivate others in the same promotion"""
    return promotion_year.activate_year(db=db, promotion_year_id=promotion_year_id)

@router.get("/{promotion_year_id}", response_model=PromotionYear)
def get_promotion_year(
    promotion_year_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific promotion year by ID"""
    promo_year = promotion_year.get(db=db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    return promo_year

@router.put("/{promotion_year_id}", response_model=PromotionYear)
def update_promotion_year(
    promotion_year_id: str,
    promotion_year_in: PromotionYearCreate,
    db: Session = Depends(get_db)
):
    """Update a promotion year"""
    promo_year = promotion_year.get(db=db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    return promotion_year.update(db=db, db_obj=promo_year, obj_in=promotion_year_in)

# PromotionYear-Service assignment endpoints
@router.post("/{promotion_year_id}/services/{service_id}", response_model=MessageResponse)
def assign_service_to_promotion_year(
    promotion_year_id: str,
    service_id: str,
    db: Session = Depends(get_db)
):
    """Assign a service to a specific year of a promotion"""
    from ...crud.service import service
    
    # Check if promotion year exists
    promo_year = promotion_year.get(db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    
    # Check if service exists
    db_service = service.get(db, id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    # Check if already assigned
    if db_service in promo_year.services:
        raise HTTPException(status_code=400, detail="Service déjà assigné à cette année")
    
    # Assign service to promotion year
    promo_year.services.append(db_service)
    db.commit()
    
    return {"message": "Service assigné à l'année de promotion avec succès"}

@router.delete("/{promotion_year_id}/services/{service_id}", response_model=MessageResponse)
def remove_service_from_promotion_year(
    promotion_year_id: str,
    service_id: str,
    db: Session = Depends(get_db)
):
    """Remove a service from a specific year of a promotion"""
    from ...crud.service import service
    
    # Check if promotion year exists
    promo_year = promotion_year.get(db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    
    # Check if service exists
    db_service = service.get(db, id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    # Check if service is assigned
    if db_service not in promo_year.services:
        raise HTTPException(status_code=400, detail="Service non assigné à cette année")
    
    # Remove service from promotion year
    promo_year.services.remove(db_service)
    db.commit()
    
    return {"message": "Service retiré de l'année de promotion avec succès"}

@router.get("/{promotion_year_id}/services", response_model=List[Service])
def get_promotion_year_services(
    promotion_year_id: str,
    db: Session = Depends(get_db)
):
    """Get all services assigned to a specific year of a promotion"""
    promo_year = promotion_year.get(db, id=promotion_year_id)
    if not promo_year:
        raise HTTPException(status_code=404, detail="Année de promotion non trouvée")
    
    return promo_year.services 
 
 