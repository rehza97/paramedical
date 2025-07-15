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
from ...crud import planning, etudiant, service as service_crud, get_advanced_planning_algorithm, rotation
from ...database import get_db
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/generer/{promo_id}", response_model=PlanningResponse)
def generate_planning(
    promo_id: str,
    promotion_year_id: str = None,  # Single year to generate planning for
    # NEW: array of years when all_years_mode is true
    promotion_year_ids: List[str] = Query(None),
    date_debut: str = None,  # Made optional - will get from database if not provided
    all_years_mode: bool = False,  # NEW: allow frontend to pass this as a query param
    db: Session = Depends(get_db)
):
    """Generate planning for a promotion"""

    # Get planning settings for default date_debut
    from ...crud.planning_settings import planning_settings
    settings = planning_settings.get_or_create_default(db)

    # Use settings start date as default
    default_date_debut = settings.academic_year_start
    logger.info(f"🔧 Default date_debut from settings: {default_date_debut}")

    # If promotion_year_id is provided, try to get year-specific date_debut
    if promotion_year_id:
        from ...models import PromotionYear
        promotion_year = db.query(PromotionYear).filter(
            PromotionYear.id == promotion_year_id,
            PromotionYear.promotion_id == promo_id
        ).first()

        if promotion_year:
            logger.info(
                f"🔧 Found promotion year: {promotion_year.nom} (ID: {promotion_year.id})")
            logger.info(
                f"🔧 Year-specific date_debut: {promotion_year.date_debut}")
            logger.info(f"🔧 Year calendar: {promotion_year.annee_calendaire}")

            # Use year-specific date if available, otherwise construct from calendar year
            if promotion_year.date_debut:
                date_debut = promotion_year.date_debut
                logger.info(f"✅ Using year-specific date_debut: {date_debut}")
            else:
                # Construct date from calendar year (e.g., 2029 -> 2029-01-01)
                date_debut = f"{promotion_year.annee_calendaire}-01-01"
                logger.info(
                    f"✅ Constructed date_debut from calendar year: {date_debut}")
        else:
            logger.warning(
                f"⚠️ Promotion year not found for ID: {promotion_year_id}")
            date_debut = default_date_debut
    else:
        # No specific year provided, use default
        date_debut = default_date_debut
        logger.info(f"✅ Using default date_debut: {date_debut}")

    # Override with provided date_debut if specified
    if date_debut:
        logger.info(f"🔧 Final date_debut: {date_debut}")
    else:
        date_debut = default_date_debut
        logger.warning(
            f"⚠️ No date_debut determined, using default: {date_debut}")

    # If all_years_mode is true and promotion_year_ids is provided, use those years
    logger.info(f"🔧 all_years_mode: {all_years_mode}")
    logger.info(f"🔧 promotion_year_ids: {promotion_year_ids}")
    logger.info(
        f"🔧 Condition check: all_years_mode={all_years_mode} and promotion_year_ids={bool(promotion_year_ids)}")

    if all_years_mode and promotion_year_ids:
        logger.info(f"✅ Entering NEW ALL YEARS MODE logic")
        # Generate ONE BIG PLANNING for all years combined
        logger.info(
            f"🔄 ALL YEARS MODE: Generating one big planning for all years: {promotion_year_ids}")

        # Get all promotion years
        from ...models import PromotionYear
        promotion_years = db.query(PromotionYear).filter(
            PromotionYear.id.in_(promotion_year_ids),
            PromotionYear.promotion_id == promo_id
        ).all()

        if not promotion_years:
            raise HTTPException(
                status_code=400,
                detail="Aucune année de promotion trouvée"
            )

        logger.info(f"✅ Found {len(promotion_years)} years to combine:")
        for year in promotion_years:
            logger.info(
                f"   - {year.nom} (ID: {year.id}, Calendar: {year.annee_calendaire})")

        # Generate one big planning that includes all years
        db_planning, number_of_services, number_of_students = planning.generate_planning_for_all_years(
            db=db,
            promo_id=promo_id,
            date_debut=date_debut,
            promotion_years=promotion_years
        )

        # Return the single big planning
        planning_dict = {
            "id": db_planning.id,
            "promo_id": db_planning.promo_id,
            "promotion_year_id": None,  # No specific year since it's combined
            "annee_niveau": None,  # No specific level since it's combined
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
                "promotion_year_id": rotation.promotion_year_id,
                "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
                "service_nom": rotation.service.nom
            }
            planning_dict["rotations"].append(rotation_dict)

        return {
            "message": "Planning généré avec succès pour toutes les années combinées",
            "planning": planning_dict,
            "number_of_services": number_of_services,
            "number_of_students": number_of_students
        }

    # Original logic for single year or all years mode
    db_planning, number_of_services, number_of_students = planning.generate_planning(
        db=db, promo_id=promo_id, date_debut=date_debut, all_years_mode=all_years_mode, promotion_year_id=promotion_year_id
    )

    if all_years_mode:
        # db_planning is a list of plannings, one per year
        plannings_list = []
        for plan in db_planning:
            planning_dict = {
                "id": plan.id,
                "promo_id": plan.promo_id,
                "promotion_year_id": plan.promotion_year_id,
                "annee_niveau": plan.annee_niveau,
                "date_creation": plan.date_creation,
                "promo_nom": plan.promotion.nom,
                "rotations": []
            }
            for rotation in plan.rotations:
                rotation_dict = {
                    "id": rotation.id,
                    "etudiant_id": rotation.etudiant_id,
                    "service_id": rotation.service_id,
                    "date_debut": rotation.date_debut,
                    "date_fin": rotation.date_fin,
                    "ordre": rotation.ordre,
                    "planning_id": rotation.planning_id,
                    "promotion_year_id": rotation.promotion_year_id,
                    "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
                    "service_nom": rotation.service.nom
                }
                planning_dict["rotations"].append(rotation_dict)
            plannings_list.append(planning_dict)
        return {
            "message": "Planning généré avec succès",
            "plannings": plannings_list,
            "number_of_services": number_of_services,
            "number_of_students": number_of_students
        }
    else:
        # Single planning (default behavior)
        planning_dict = {
            "id": db_planning.id,
            "promo_id": db_planning.promo_id,
            "promotion_year_id": db_planning.promotion_year_id,
            "annee_niveau": db_planning.annee_niveau,
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
                "promotion_year_id": rotation.promotion_year_id,
                "etudiant_nom": f"{rotation.etudiant.prenom} {rotation.etudiant.nom}",
                "service_nom": rotation.service.nom
            }
            planning_dict["rotations"].append(rotation_dict)
        return {
            "message": "Planning généré avec succès",
            "planning": planning_dict,
            "number_of_services": number_of_services,
            "number_of_students": number_of_students
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
            "promotion_year_id": rotation.promotion_year_id,
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
