from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime

from ...database import get_db
from ...crud import planning, etudiant, service as service_crud, get_advanced_planning_algorithm, rotation
from ...schemas import (
    Planning,
    PlanningResponse,
    StudentPlanningResponse,
    AdvancedPlanningRequest,
    AdvancedPlanningResponse,
    PlanningEfficiencyAnalysis,
    PlanningValidationResult,
    RotationUpdate,
    MessageResponse,
    Promotion
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


@router.put("/rotation/{rotation_id}", response_model=MessageResponse)
def update_rotation(
    rotation_id: str,
    rotation_update: RotationUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific rotation"""
    try:
        # Get the existing rotation
        db_rotation = rotation.get(db, id=rotation_id)
        if not db_rotation:
            raise HTTPException(status_code=404, detail="Rotation non trouvée")

        # Validate the service exists if provided
        if rotation_update.service_id:
            service = service_crud.get(db, id=rotation_update.service_id)
            if not service:
                raise HTTPException(
                    status_code=404, detail="Service non trouvé")

        # Validate the student exists if provided
        if rotation_update.etudiant_id:
            student = etudiant.get(db, id=rotation_update.etudiant_id)
            if not student:
                raise HTTPException(
                    status_code=404, detail="Étudiant non trouvé")

        # Only update fields that are provided (not None)
        update_data = rotation_update.dict(exclude_unset=True)

        # Update the rotation
        updated_rotation = rotation.update(
            db, db_obj=db_rotation, obj_in=update_data)

        return {"message": "Rotation mise à jour avec succès"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.get("/{promo_id}/export")
def export_planning_excel(
    promo_id: str,
    db: Session = Depends(get_db)
):
    """Export planning to Excel format"""
    try:
        # Get the planning for this promotion
        db_planning = planning.get_by_promotion(db, promo_id=promo_id)
        if not db_planning:
            raise HTTPException(status_code=404, detail="Planning non trouvé")

        # Prepare data for Excel export
        rotations_data = []
        for rotation in db_planning.rotations:
            # Calculate duration
            try:
                start_date = datetime.strptime(rotation.date_debut, "%Y-%m-%d")
                end_date = datetime.strptime(rotation.date_fin, "%Y-%m-%d")
                duration_days = (end_date - start_date).days + 1
                duration_weeks = round(duration_days / 7, 1)
            except ValueError:
                duration_days = 0
                duration_weeks = 0

            rotation_data = {
                "Étudiant": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
                "Service": rotation.service.nom,
                "Date début": rotation.date_debut,
                "Date fin": rotation.date_fin,
                "Durée (jours)": duration_days,
                "Durée (semaines)": duration_weeks,
                "Ordre rotation": rotation.ordre,
                "Spécialité": rotation.service.speciality.nom if rotation.service.speciality else "Non définie",
                "Places disponibles": rotation.service.places_disponibles,
                "Durée standard (jours)": rotation.service.duree_stage_jours
            }
            rotations_data.append(rotation_data)

        # Create DataFrame
        df_rotations = pd.DataFrame(rotations_data)

        # Sort by student name and then by rotation order
        df_rotations = df_rotations.sort_values(['Étudiant', 'Ordre rotation'])

        # Create summary statistics
        summary_data = {
            "Métrique": [
                "Nombre total d'étudiants",
                "Nombre total de rotations",
                "Nombre de services utilisés",
                "Durée moyenne par rotation (jours)",
                "Date de début du planning",
                "Date de fin du planning",
                "Promotion",
                "Spécialité de la promotion"
            ],
            "Valeur": [
                df_rotations['Étudiant'].nunique(),
                len(df_rotations),
                df_rotations['Service'].nunique(),
                round(df_rotations['Durée (jours)'].mean(),
                      1) if len(df_rotations) > 0 else 0,
                df_rotations['Date début'].min() if len(
                    df_rotations) > 0 else "N/A",
                df_rotations['Date fin'].max() if len(
                    df_rotations) > 0 else "N/A",
                db_planning.promotion.nom,
                db_planning.promotion.speciality.nom if db_planning.promotion.speciality else "Non définie"
            ]
        }
        df_summary = pd.DataFrame(summary_data)

        # Create service utilization statistics
        service_stats = df_rotations.groupby('Service').agg({
            'Étudiant': 'count',
            'Durée (jours)': ['sum', 'mean'],
            'Places disponibles': 'first'
        }).round(1)

        service_stats.columns = [
            'Nombre étudiants', 'Durée totale (jours)', 'Durée moyenne (jours)', 'Places disponibles']
        service_stats['Taux occupation (%)'] = round(
            (service_stats['Nombre étudiants'] / service_stats['Places disponibles']) * 100, 1)
        service_stats = service_stats.reset_index()

        # Create student summary
        student_stats = df_rotations.groupby('Étudiant').agg({
            'Service': 'count',
            'Durée (jours)': 'sum',
            'Ordre rotation': ['min', 'max']
        }).round(1)

        student_stats.columns = [
            'Nombre de services', 'Durée totale (jours)', 'Première rotation', 'Dernière rotation']
        student_stats['Durée totale (semaines)'] = round(
            student_stats['Durée totale (jours)'] / 7, 1)
        student_stats = student_stats.reset_index()

        # Create Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write different sheets
            df_rotations.to_excel(
                writer, sheet_name='Rotations détaillées', index=False)
            df_summary.to_excel(
                writer, sheet_name='Résumé du planning', index=False)
            service_stats.to_excel(
                writer, sheet_name='Statistiques services', index=False)
            student_stats.to_excel(
                writer, sheet_name='Statistiques étudiants', index=False)

            # Simple formatting for openpyxl
            workbook = writer.book

            # Auto-adjust column widths for all sheets
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 30)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

        output.seek(0)

        # Generate filename with promotion name and current date
        current_date = datetime.now().strftime("%Y%m%d_%H%M")
        promotion_name = db_planning.promotion.nom.replace(" ", "_")
        filename = f"planning_{promotion_name}_{current_date}.xlsx"

        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'export: {str(e)}"
        )


@router.get("/{planning_id}/promotions", response_model=List[Promotion])
def get_promotions_for_planning(
    planning_id: str,
    db: Session = Depends(get_db)
):
    """Get all promotions associated with a specific planning"""
    try:
        from ...models import Planning, Promotion

        # Get the planning
        db_planning = db.query(Planning).filter(
            Planning.id == planning_id).first()
        if not db_planning:
            raise HTTPException(status_code=404, detail="Planning non trouvé")

        # Get the promotion associated with this planning
        promotion = db.query(Promotion).filter(
            Promotion.id == db_planning.promo_id).first()
        if not promotion:
            raise HTTPException(
                status_code=404, detail="Promotion non trouvée")

        # Return the promotion (since each planning belongs to one promotion)
        return [promotion]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des promotions: {str(e)}"
        )


@router.get("/{planning_id}/details", response_model=dict)
def get_planning_details(
    planning_id: str,
    db: Session = Depends(get_db)
):
    """Get planning details with promotion information"""
    try:
        from ...models import Planning, Promotion

        # Get the planning with promotion info
        db_planning = db.query(Planning).filter(
            Planning.id == planning_id).first()
        if not db_planning:
            raise HTTPException(status_code=404, detail="Planning non trouvé")

        # Get the promotion
        promotion = db.query(Promotion).filter(
            Promotion.id == db_planning.promo_id).first()
        if not promotion:
            raise HTTPException(
                status_code=404, detail="Promotion non trouvée")

        return {
            "planning_id": db_planning.id,
            "promotion_id": promotion.id,
            "promotion_name": promotion.nom,
            "planning_creation_date": db_planning.date_creation.isoformat() if db_planning.date_creation else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des détails du planning: {str(e)}"
        )


@router.get("/{planning_id}/validate", response_model=PlanningValidationResult)
def validate_planning(
    planning_id: str,
    db: Session = Depends(get_db)
):
    """Validate a planning and return warnings/conflicts"""
    result = rotation.validate_all_assignments(db, planning_id=planning_id)
    # The result dict may have keys 'is_valid', 'erreurs', 'warnings', etc.
    # Map 'erreurs' to 'errors' and ensure 'warnings' is present
    return {
        "is_valid": result.get("is_valid", False),
        "erreurs": result.get("erreurs", []),
        "warnings": result.get("warnings", []),
    }
