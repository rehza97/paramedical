from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud import planning, etudiant, service as service_crud, get_advanced_planning_algorithm
from ...schemas import (
    Planning, 
    PlanningResponse, 
    StudentPlanningResponse,
    AdvancedPlanningRequest,
    AdvancedPlanningResponse,
    PlanningEfficiencyAnalysis,
    PlanningValidationResult
)

router = APIRouter()

@router.post("/generer/{promo_id}", response_model=PlanningResponse)
def generate_planning(
    promo_id: str,
    date_debut: str = "2025-01-01",
    db: Session = Depends(get_db)
):
    """Generate planning for a promotion"""
    db_planning = planning.generate_planning(
        db=db, promo_id=promo_id, date_debut=date_debut
    )
    
    # Convert to response format
    planning_dict = {
        "id": db_planning.id,
        "promo_id": db_planning.promo_id,
        "date_creation": db_planning.date_creation,
        "promo_nom": db_planning.promotion.nom,
        "rotations": []
    }
    
    # Add rotation details with student and service names
    for rotation in db_planning.rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        planning_dict["rotations"].append(rotation_dict)
    
    return {
        "message": "Planning généré avec succès",
        "planning": planning_dict
    }

@router.post("/generer-avance/{promo_id}", response_model=AdvancedPlanningResponse)
def generate_advanced_planning(
    promo_id: str,
    date_debut: str = "2025-01-01",
    db: Session = Depends(get_db)
):
    """
    Generate planning using advanced algorithm with intelligent load balancing
    Includes efficiency analysis and validation
    """
    advanced_algo = get_advanced_planning_algorithm(db)
    
    planning_result, efficiency_analysis, validation_result = advanced_algo.generate_advanced_planning(
        promo_id=promo_id,
        date_debut_str=date_debut
    )
    
    return AdvancedPlanningResponse(
        message="Planning avancé généré avec succès",
        planning=planning_result,
        efficiency_analysis=efficiency_analysis,
        validation_result=validation_result
    )

@router.post("/analyser-efficacite/{promo_id}", response_model=PlanningEfficiencyAnalysis)
def analyze_planning_efficiency(
    promo_id: str,
    db: Session = Depends(get_db)
):
    """Analyze the efficiency of an existing planning"""
    # Get existing planning
    db_planning = planning.get_by_promotion(db, promo_id=promo_id)
    if not db_planning:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    
    # Get services
    services = db.query(service_crud.model).all()
    services_list = [
        {
            'id': s.id,
            'nom': s.nom,
            'places_disponibles': s.places_disponibles,
            'duree_stage_jours': s.duree_stage_jours
        } for s in services
    ]
    
    # Convert planning to schema format
    planning_schema = {
        "id": db_planning.id,
        "promo_id": db_planning.promo_id,
        "date_creation": db_planning.date_creation,
        "promo_nom": db_planning.promotion.nom,
        "rotations": []
    }
    
    for rotation in db_planning.rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        planning_schema["rotations"].append(rotation_dict)
    
    # Analyze efficiency
    advanced_algo = get_advanced_planning_algorithm(db)
    from ...schemas import Planning as PlanningSchema
    planning_obj = PlanningSchema(**planning_schema)
    
    return advanced_algo._analyser_efficacite_planning(planning_obj, services_list)

@router.post("/valider/{promo_id}", response_model=PlanningValidationResult)
def validate_planning(
    promo_id: str,
    db: Session = Depends(get_db)
):
    """Validate an existing planning and return any errors"""
    # Get existing planning
    db_planning = planning.get_by_promotion(db, promo_id=promo_id)
    if not db_planning:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    
    # Get services
    services = db.query(service_crud.model).all()
    services_list = [
        {
            'id': s.id,
            'nom': s.nom,
            'places_disponibles': s.places_disponibles,
            'duree_stage_jours': s.duree_stage_jours
        } for s in services
    ]
    
    # Convert planning to schema format
    planning_schema = {
        "id": db_planning.id,
        "promo_id": db_planning.promo_id,
        "date_creation": db_planning.date_creation,
        "promo_nom": db_planning.promotion.nom,
        "rotations": []
    }
    
    for rotation in db_planning.rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        planning_schema["rotations"].append(rotation_dict)
    
    # Validate planning
    advanced_algo = get_advanced_planning_algorithm(db)
    from ...schemas import Planning as PlanningSchema
    planning_obj = PlanningSchema(**planning_schema)
    
    return advanced_algo._valider_planning(planning_obj, services_list)

@router.get("/{promo_id}", response_model=Planning)
def get_planning(
    promo_id: str,
    db: Session = Depends(get_db)
):
    """Get planning for a promotion"""
    db_planning = planning.get_by_promotion(db, promo_id=promo_id)
    if not db_planning:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    
    # Add promotion name and student/service names to rotations
    planning_dict = {
        "id": db_planning.id,
        "promo_id": db_planning.promo_id,
        "date_creation": db_planning.date_creation,
        "promo_nom": db_planning.promotion.nom,
        "rotations": []
    }
    
    for rotation in db_planning.rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        planning_dict["rotations"].append(rotation_dict)
    
    return planning_dict

@router.get("/etudiant/{promo_id}/{etudiant_id}", response_model=StudentPlanningResponse)
def get_student_planning(
    promo_id: str,
    etudiant_id: str,
    db: Session = Depends(get_db)
):
    """Get planning for a specific student"""
    rotations = planning.get_student_planning(
        db=db, promo_id=promo_id, etudiant_id=etudiant_id
    )
    
    # Add student and service names
    rotations_with_names = []
    for rotation in rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        rotations_with_names.append(rotation_dict)
    
    return {
        "etudiant_id": etudiant_id,
        "rotations": rotations_with_names
    } 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...crud import planning, etudiant, service as service_crud, get_advanced_planning_algorithm
from ...schemas import (
    Planning, 
    PlanningResponse, 
    StudentPlanningResponse,
    AdvancedPlanningRequest,
    AdvancedPlanningResponse,
    PlanningEfficiencyAnalysis,
    PlanningValidationResult
)

router = APIRouter()

@router.post("/generer/{promo_id}", response_model=PlanningResponse)
def generate_planning(
    promo_id: str,
    date_debut: str = "2025-01-01",
    db: Session = Depends(get_db)
):
    """Generate planning for a promotion"""
    db_planning = planning.generate_planning(
        db=db, promo_id=promo_id, date_debut=date_debut
    )
    
    # Convert to response format
    planning_dict = {
        "id": db_planning.id,
        "promo_id": db_planning.promo_id,
        "date_creation": db_planning.date_creation,
        "promo_nom": db_planning.promotion.nom,
        "rotations": []
    }
    
    # Add rotation details with student and service names
    for rotation in db_planning.rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        planning_dict["rotations"].append(rotation_dict)
    
    return {
        "message": "Planning généré avec succès",
        "planning": planning_dict
    }

@router.post("/generer-avance/{promo_id}", response_model=AdvancedPlanningResponse)
def generate_advanced_planning(
    promo_id: str,
    date_debut: str = "2025-01-01",
    db: Session = Depends(get_db)
):
    """
    Generate planning using advanced algorithm with intelligent load balancing
    Includes efficiency analysis and validation
    """
    advanced_algo = get_advanced_planning_algorithm(db)
    
    planning_result, efficiency_analysis, validation_result = advanced_algo.generate_advanced_planning(
        promo_id=promo_id,
        date_debut_str=date_debut
    )
    
    return AdvancedPlanningResponse(
        message="Planning avancé généré avec succès",
        planning=planning_result,
        efficiency_analysis=efficiency_analysis,
        validation_result=validation_result
    )

@router.post("/analyser-efficacite/{promo_id}", response_model=PlanningEfficiencyAnalysis)
def analyze_planning_efficiency(
    promo_id: str,
    db: Session = Depends(get_db)
):
    """Analyze the efficiency of an existing planning"""
    # Get existing planning
    db_planning = planning.get_by_promotion(db, promo_id=promo_id)
    if not db_planning:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    
    # Get services
    services = db.query(service_crud.model).all()
    services_list = [
        {
            'id': s.id,
            'nom': s.nom,
            'places_disponibles': s.places_disponibles,
            'duree_stage_jours': s.duree_stage_jours
        } for s in services
    ]
    
    # Convert planning to schema format
    planning_schema = {
        "id": db_planning.id,
        "promo_id": db_planning.promo_id,
        "date_creation": db_planning.date_creation,
        "promo_nom": db_planning.promotion.nom,
        "rotations": []
    }
    
    for rotation in db_planning.rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        planning_schema["rotations"].append(rotation_dict)
    
    # Analyze efficiency
    advanced_algo = get_advanced_planning_algorithm(db)
    from ...schemas import Planning as PlanningSchema
    planning_obj = PlanningSchema(**planning_schema)
    
    return advanced_algo._analyser_efficacite_planning(planning_obj, services_list)

@router.post("/valider/{promo_id}", response_model=PlanningValidationResult)
def validate_planning(
    promo_id: str,
    db: Session = Depends(get_db)
):
    """Validate an existing planning and return any errors"""
    # Get existing planning
    db_planning = planning.get_by_promotion(db, promo_id=promo_id)
    if not db_planning:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    
    # Get services
    services = db.query(service_crud.model).all()
    services_list = [
        {
            'id': s.id,
            'nom': s.nom,
            'places_disponibles': s.places_disponibles,
            'duree_stage_jours': s.duree_stage_jours
        } for s in services
    ]
    
    # Convert planning to schema format
    planning_schema = {
        "id": db_planning.id,
        "promo_id": db_planning.promo_id,
        "date_creation": db_planning.date_creation,
        "promo_nom": db_planning.promotion.nom,
        "rotations": []
    }
    
    for rotation in db_planning.rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        planning_schema["rotations"].append(rotation_dict)
    
    # Validate planning
    advanced_algo = get_advanced_planning_algorithm(db)
    from ...schemas import Planning as PlanningSchema
    planning_obj = PlanningSchema(**planning_schema)
    
    return advanced_algo._valider_planning(planning_obj, services_list)

@router.get("/{promo_id}", response_model=Planning)
def get_planning(
    promo_id: str,
    db: Session = Depends(get_db)
):
    """Get planning for a promotion"""
    db_planning = planning.get_by_promotion(db, promo_id=promo_id)
    if not db_planning:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    
    # Add promotion name and student/service names to rotations
    planning_dict = {
        "id": db_planning.id,
        "promo_id": db_planning.promo_id,
        "date_creation": db_planning.date_creation,
        "promo_nom": db_planning.promotion.nom,
        "rotations": []
    }
    
    for rotation in db_planning.rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        planning_dict["rotations"].append(rotation_dict)
    
    return planning_dict

@router.get("/etudiant/{promo_id}/{etudiant_id}", response_model=StudentPlanningResponse)
def get_student_planning(
    promo_id: str,
    etudiant_id: str,
    db: Session = Depends(get_db)
):
    """Get planning for a specific student"""
    rotations = planning.get_student_planning(
        db=db, promo_id=promo_id, etudiant_id=etudiant_id
    )
    
    # Add student and service names
    rotations_with_names = []
    for rotation in rotations:
        rotation_dict = {
            "id": rotation.id,
            "etudiant_id": rotation.etudiant_id,
            "service_id": rotation.service_id,
            "date_debut": rotation.date_debut,
            "date_fin": rotation.date_fin,
            "ordre": rotation.ordre,
            "planning_id": rotation.planning_id,
            "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
            "service_nom": rotation.service.nom
        }
        rotations_with_names.append(rotation_dict)
    
    return {
        "etudiant_id": etudiant_id,
        "rotations": rotations_with_names
    } 
 
 