from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from app.database import get_db, engine
import app.models as models
import app.schemas as schemas

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "stages-paramedicaux-api"}

# Gestion des Promotions


@app.post("/api/promotions", response_model=schemas.IdResponse)
async def create_promotion(promotion: schemas.PromotionCreate, db: Session = Depends(get_db)):
    # Validation: must have at least one student
    if not promotion.etudiants or len(promotion.etudiants) == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="La promotion doit contenir au moins un étudiant.")
    db_promotion = models.Promotion(
        id=str(uuid.uuid4()),
        nom=promotion.nom,
        annee=promotion.annee
    )
    db.add(db_promotion)
    db.flush()  # Get the promotion ID
    for etudiant_data in promotion.etudiants:
        db_etudiant = models.Etudiant(
            id=str(uuid.uuid4()),
            nom=etudiant_data.nom,
            prenom=etudiant_data.prenom,
            promotion_id=db_promotion.id
        )
        db.add(db_etudiant)
    db.commit()
    return {"id": db_promotion.id, "message": "Promotion créée avec succès"}


@app.get("/api/promotions", response_model=List[schemas.Promotion])
async def get_promotions(db: Session = Depends(get_db)):
    promotions = db.query(models.Promotion).all()
    return promotions


@app.get("/api/promotions/{promo_id}", response_model=schemas.Promotion)
async def get_promotion(promo_id: str, db: Session = Depends(get_db)):
    promotion = db.query(models.Promotion).filter(
        models.Promotion.id == promo_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")
    return promotion


@app.delete("/api/promotions/{promo_id}", response_model=schemas.MessageResponse)
async def delete_promotion(promo_id: str, db: Session = Depends(get_db)):
    promotion = db.query(models.Promotion).filter(
        models.Promotion.id == promo_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    # First, delete all rotations associated with plannings of this promotion
    plannings = db.query(models.Planning).filter(
        models.Planning.promo_id == promo_id).all()
    for planning in plannings:
        # Delete rotations for this planning
        db.query(models.Rotation).filter(
            models.Rotation.planning_id == planning.id).delete()

    # Then delete the plannings
    db.query(models.Planning).filter(
        models.Planning.promo_id == promo_id).delete()

    # Delete promotion (cascade will handle students)
    db.delete(promotion)
    db.commit()

    return {"message": "Promotion supprimée avec succès"}

# Gestion des Spécialités


@app.post("/api/specialities", response_model=schemas.IdResponse)
async def create_speciality(speciality: schemas.SpecialityCreate, db: Session = Depends(get_db)):
    # Check if speciality name already exists
    existing_speciality = db.query(models.Speciality).filter(
        models.Speciality.nom == speciality.nom).first()
    if existing_speciality:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Le nom de la spécialité doit être unique.")

    db_speciality = models.Speciality(
        id=str(uuid.uuid4()),
        nom=speciality.nom,
        description=speciality.description,
        duree_annees=speciality.duree_annees
    )
    db.add(db_speciality)
    db.commit()
    return {"id": db_speciality.id, "message": "Spécialité créée avec succès"}


@app.get("/api/specialities", response_model=List[schemas.Speciality])
async def get_specialities(db: Session = Depends(get_db)):
    specialities = db.query(models.Speciality).all()
    return specialities


@app.get("/api/specialities/{speciality_id}", response_model=schemas.Speciality)
async def get_speciality(speciality_id: str, db: Session = Depends(get_db)):
    speciality = db.query(models.Speciality).filter(
        models.Speciality.id == speciality_id).first()
    if not speciality:
        raise HTTPException(status_code=404, detail="Spécialité non trouvée")
    return speciality


@app.put("/api/specialities/{speciality_id}", response_model=schemas.MessageResponse)
async def update_speciality(speciality_id: str, speciality: schemas.SpecialityCreate, db: Session = Depends(get_db)):
    db_speciality = db.query(models.Speciality).filter(
        models.Speciality.id == speciality_id).first()
    if not db_speciality:
        raise HTTPException(status_code=404, detail="Spécialité non trouvée")

    # Check if new name conflicts with existing speciality (excluding current one)
    existing_speciality = db.query(models.Speciality).filter(
        models.Speciality.nom == speciality.nom,
        models.Speciality.id != speciality_id
    ).first()
    if existing_speciality:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Le nom de la spécialité doit être unique.")

    db_speciality.nom = speciality.nom
    db_speciality.description = speciality.description
    db_speciality.duree_annees = speciality.duree_annees

    db.commit()
    return {"message": "Spécialité mise à jour avec succès"}


@app.delete("/api/specialities/{speciality_id}", response_model=schemas.MessageResponse)
async def delete_speciality(speciality_id: str, db: Session = Depends(get_db)):
    speciality = db.query(models.Speciality).filter(
        models.Speciality.id == speciality_id).first()
    if not speciality:
        raise HTTPException(status_code=404, detail="Spécialité non trouvée")

    # Check if speciality is used by any promotions
    promotions_count = db.query(models.Promotion).filter(
        models.Promotion.speciality_id == speciality_id).count()
    if promotions_count > 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Impossible de supprimer la spécialité car elle est utilisée par {promotions_count} promotion(s).")

    db.delete(speciality)
    db.commit()
    return {"message": "Spécialité supprimée avec succès"}

# Gestion des Services


@app.post("/api/services", response_model=schemas.IdResponse)
async def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    # Validation: places_disponibles and duree_stage_jours must be positive
    if service.places_disponibles < 1 or service.duree_stage_jours < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Les valeurs doivent être positives et supérieures à zéro.")
    db_service = models.Service(
        id=str(uuid.uuid4()),
        nom=service.nom,
        places_disponibles=service.places_disponibles,
        duree_stage_jours=service.duree_stage_jours
    )
    db.add(db_service)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Le nom du service doit être unique.")
    return {"id": db_service.id, "message": "Service créé avec succès"}


@app.get("/api/services", response_model=List[schemas.Service])
async def get_services(db: Session = Depends(get_db)):
    services = db.query(models.Service).all()
    return services


@app.put("/api/services/{service_id}", response_model=schemas.MessageResponse)
async def update_service(service_id: str, service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    db_service = db.query(models.Service).filter(
        models.Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service non trouvé")

    db_service.nom = service.nom
    db_service.places_disponibles = service.places_disponibles
    db_service.duree_stage_jours = service.duree_stage_jours

    db.commit()
    return {"message": "Service mis à jour avec succès"}


@app.delete("/api/services/{service_id}", response_model=schemas.MessageResponse)
async def delete_service(service_id: str, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(
        models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")

    db.delete(service)
    db.commit()
    return {"message": "Service supprimé avec succès"}

# Gestion des associations Promotion-Service


@app.post("/api/promotions/{promo_id}/services/{service_id}", response_model=schemas.MessageResponse)
async def assign_service_to_promotion(promo_id: str, service_id: str, db: Session = Depends(get_db)):
    # Check if promotion exists
    promotion = db.query(models.Promotion).filter(
        models.Promotion.id == promo_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    # Check if service exists
    service = db.query(models.Service).filter(
        models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")

    # Check if association already exists
    if service in promotion.services:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Ce service est déjà assigné à cette promotion")

    # Add the service to the promotion
    promotion.services.append(service)
    db.commit()

    return {"message": f"Service '{service.nom}' assigné à la promotion '{promotion.nom}' avec succès"}


@app.delete("/api/promotions/{promo_id}/services/{service_id}", response_model=schemas.MessageResponse)
async def remove_service_from_promotion(promo_id: str, service_id: str, db: Session = Depends(get_db)):
    # Check if promotion exists
    promotion = db.query(models.Promotion).filter(
        models.Promotion.id == promo_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    # Check if service exists
    service = db.query(models.Service).filter(
        models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")

    # Check if association exists
    if service not in promotion.services:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Ce service n'est pas assigné à cette promotion")

    # Remove the service from the promotion
    promotion.services.remove(service)
    db.commit()

    return {"message": f"Service '{service.nom}' retiré de la promotion '{promotion.nom}' avec succès"}


@app.get("/api/promotions/{promo_id}/services", response_model=List[schemas.Service])
async def get_promotion_services(promo_id: str, db: Session = Depends(get_db)):
    promotion = db.query(models.Promotion).filter(
        models.Promotion.id == promo_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    return promotion.services

# Gestion des Plannings


@app.post("/api/plannings/generer/{promo_id}", response_model=schemas.PlanningResponse)
async def generer_planning(promo_id: str, date_debut: str = "2025-01-01", db: Session = Depends(get_db)):
    # Récupérer la promotion et les services
    promotion = db.query(models.Promotion).filter(
        models.Promotion.id == promo_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion non trouvée")

    services = db.query(models.Service).all()
    if not services:
        raise HTTPException(status_code=400, detail="Aucun service configuré")

    # Supprimer l'ancien planning s'il existe
    db.query(models.Planning).filter(
        models.Planning.promo_id == promo_id).delete()

    # Générer le nouveau planning
    planning = generer_algorithme_repartition(
        promotion, services, date_debut, db)

    return {"message": "Planning généré avec succès", "planning": planning}


@app.get("/api/plannings/{promo_id}", response_model=schemas.Planning)
async def get_planning(promo_id: str, db: Session = Depends(get_db)):
    planning = db.query(models.Planning).filter(
        models.Planning.promo_id == promo_id).first()
    if not planning:
        raise HTTPException(status_code=404, detail="Planning non trouvé")

    # Add promotion name and student/service names to rotations
    planning_dict = schemas.Planning.model_validate(
        planning, from_attributes=True).model_dump()
    planning_dict["promo_nom"] = planning.promotion.nom

    for rotation in planning_dict["rotations"]:
        # Get student name
        etudiant = db.query(models.Etudiant).filter(
            models.Etudiant.id == rotation["etudiant_id"]).first()
        if etudiant:
            rotation["etudiant_nom"] = f"{etudiant.prenom} {etudiant.nom}"

        # Get service name
        service = db.query(models.Service).filter(
            models.Service.id == rotation["service_id"]).first()
        if service:
            rotation["service_nom"] = service.nom

    return planning_dict


@app.get("/api/plannings/etudiant/{promo_id}/{etudiant_id}", response_model=schemas.StudentPlanningResponse)
async def get_planning_etudiant(promo_id: str, etudiant_id: str, db: Session = Depends(get_db)):
    planning = db.query(models.Planning).filter(
        models.Planning.promo_id == promo_id).first()
    if not planning:
        raise HTTPException(status_code=404, detail="Planning non trouvé")

    rotations = db.query(models.Rotation).filter(
        models.Rotation.planning_id == planning.id,
        models.Rotation.etudiant_id == etudiant_id
    ).order_by(models.Rotation.ordre).all()

    # Add student and service names
    rotations_with_names = []
    for rotation in rotations:
        rotation_dict = schemas.Rotation.model_validate(
            rotation, from_attributes=True).model_dump()

        # Get student name
        etudiant = db.query(models.Etudiant).filter(
            models.Etudiant.id == rotation.etudiant_id).first()
        if etudiant:
            rotation_dict["etudiant_nom"] = f"{etudiant.prenom} {etudiant.nom}"

        # Get service name
        service = db.query(models.Service).filter(
            models.Service.id == rotation.service_id).first()
        if service:
            rotation_dict["service_nom"] = service.nom

        rotations_with_names.append(rotation_dict)

    return {
        "etudiant_id": etudiant_id,
        "rotations": rotations_with_names
    }


def generer_algorithme_repartition(promotion: models.Promotion, services: List[models.Service], date_debut_str: str, db: Session) -> schemas.Planning:
    """
    Algorithme de répartition automatique des stages - Version PostgreSQL
    Garantit que chaque étudiant passe par tous les services
    """
    etudiants = promotion.etudiants
    nb_etudiants = len(etudiants)
    nb_services = len(services)

    if nb_services == 0:
        raise HTTPException(status_code=400, detail="Aucun service disponible")

    # Trier les services par nom pour avoir un ordre cohérent
    services_sorted = sorted(services, key=lambda x: x.nom)

    date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")

    # Créer le planning
    db_planning = models.Planning(
        id=str(uuid.uuid4()),
        promo_id=promotion.id
    )
    db.add(db_planning)
    db.flush()  # Get the planning ID

    # Pour chaque étudiant, créer sa séquence complète de stages
    for idx_etudiant, etudiant in enumerate(etudiants):
        date_debut_etudiant = date_debut

        # Décaler la date de début pour éviter que tous les étudiants commencent en même temps
        min_places = min([s.places_disponibles for s in services_sorted])
        decalage_jours = (idx_etudiant // min_places) * \
            7  # Nouveau groupe tous les 7 jours
        date_debut_etudiant = date_debut + timedelta(days=decalage_jours)

        # Pour cet étudiant, créer une rotation dans chaque service
        date_courante_etudiant = date_debut_etudiant

        for ordre_service, service in enumerate(services_sorted):
            duree_jours = service.duree_stage_jours

            date_fin_stage = date_courante_etudiant + \
                timedelta(days=duree_jours - 1)

            rotation = models.Rotation(
                id=str(uuid.uuid4()),
                etudiant_id=etudiant.id,
                service_id=service.id,
                date_debut=date_courante_etudiant.strftime("%Y-%m-%d"),
                date_fin=date_fin_stage.strftime("%Y-%m-%d"),
                ordre=ordre_service + 1,
                planning_id=db_planning.id
            )
            db.add(rotation)

            # Avancer à la date de fin + 1 jour pour le prochain service
            date_courante_etudiant = date_fin_stage + timedelta(days=1)

    db.commit()

    # Return the planning with all relationships loaded
    db.refresh(db_planning)
    return schemas.Planning.model_validate(db_planning, from_attributes=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
