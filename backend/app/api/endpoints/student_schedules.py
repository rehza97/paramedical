from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io
import pandas as pd

from ...database import get_db
from ...crud import student_schedule, student_schedule_detail
from ...models import StudentSchedule, StudentScheduleDetail
from ...schemas import (
    StudentSchedule,
    StudentScheduleCreate,
    StudentScheduleUpdate,
    StudentScheduleDetail,
    StudentScheduleDetailCreate,
    StudentScheduleSummary,
    StudentScheduleProgress,
    MessageResponse
)

router = APIRouter()


@router.get("/etudiant/{etudiant_id}", response_model=StudentSchedule)
def get_student_schedule(
    etudiant_id: str,
    db: Session = Depends(get_db)
):
    """Get the active schedule for a student"""
    schedule = student_schedule.get_active_by_etudiant(
        db, etudiant_id=etudiant_id)
    if not schedule:
        raise HTTPException(
            status_code=404, detail="Aucun planning actif trouvé")

    # Add student name
    schedule.etudiant_nom = f"{schedule.etudiant.prenom} {schedule.etudiant.nom}"

    return schedule


@router.get("/etudiant/{etudiant_id}/historique", response_model=List[StudentSchedule])
def get_student_schedule_history(
    etudiant_id: str,
    db: Session = Depends(get_db)
):
    """Get all schedules (including archived) for a student"""
    schedules = student_schedule.get_by_etudiant(db, etudiant_id=etudiant_id)

    # Add student names
    for schedule in schedules:
        schedule.etudiant_nom = f"{schedule.etudiant.prenom} {schedule.etudiant.nom}"

    return schedules


@router.get("/etudiant/{etudiant_id}/progression", response_model=StudentScheduleProgress)
def get_student_progress(
    etudiant_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive progress summary for a student"""
    return student_schedule.get_progress_summary(db, etudiant_id=etudiant_id)


@router.put("/{schedule_id}/service/{service_id}/statut", response_model=MessageResponse)
def update_service_status(
    schedule_id: str,
    service_id: str,
    update_data: StudentScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update the status of a specific service in a student's schedule"""
    schedule_detail = student_schedule.update_progress(
        db=db,
        schedule_id=schedule_id,
        service_id=service_id,
        new_statut=update_data.statut,
        notes=update_data.notes
    )

    return {"message": f"Statut du service '{schedule_detail.service_nom}' mis à jour avec succès"}


@router.get("/planning/{planning_id}/resume", response_model=List[StudentScheduleSummary])
def get_planning_summary(
    planning_id: str,
    db: Session = Depends(get_db)
):
    """Get summary of all student schedules in a planning"""
    return student_schedule.get_summary_by_planning(db, planning_id=planning_id)


@router.get("/promotion/{promotion_id}", response_model=List[StudentScheduleSummary])
def get_student_schedules_by_promotion(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Get all student schedules for a specific promotion"""
    try:
        # Get all students in the promotion
        from ...models import Etudiant
        students = db.query(Etudiant).filter(
            Etudiant.promotion_id == promotion_id).all()

        schedules = []
        for student in students:
            # Get the active schedule for each student
            schedule = student_schedule.get_active_by_etudiant(
                db, etudiant_id=student.id)
            if schedule:
                # Create summary object
                summary = StudentScheduleSummary(
                    id=schedule.id,
                    etudiant_id=student.id,
                    etudiant_nom=f"{student.prenom} {student.nom}",
                    etudiant_prenom=student.prenom,
                    planning_id=schedule.planning_id,
                    date_debut_planning=schedule.date_debut_planning,
                    date_fin_planning=schedule.date_fin_planning,
                    nb_services_total=schedule.nb_services_total,
                    nb_services_completes=schedule.nb_services_completes,
                    duree_totale_jours=schedule.duree_totale_jours,
                    statut=schedule.statut,
                    progression=float(schedule.nb_services_completes) / float(
                        schedule.nb_services_total) * 100 if schedule.nb_services_total > 0 else 0.0
                )
                schedules.append(summary)
            else:
                # Create empty summary for students without schedules
                summary = StudentScheduleSummary(
                    id="",
                    etudiant_id=student.id,
                    etudiant_nom=f"{student.prenom} {student.nom}",
                    etudiant_prenom=student.prenom,
                    planning_id="",
                    date_debut_planning="",
                    date_fin_planning="",
                    nb_services_total=0,
                    nb_services_completes=0,
                    duree_totale_jours=0,
                    statut="non_planifie",
                    progression=0.0
                )
                schedules.append(summary)

        return schedules
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la récupération des plannings: {str(e)}")


@router.post("/{schedule_id}/archiver", response_model=MessageResponse)
def archive_schedule(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    """Archive a student schedule (mark as inactive)"""
    student_schedule.archive_schedule(db, schedule_id=schedule_id)
    return {"message": "Planning archivé avec succès"}


@router.post("/{schedule_id}/nouvelle-version", response_model=StudentSchedule)
def create_schedule_version(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    """Create a new version of an existing schedule"""
    return student_schedule.create_new_version(db, schedule_id=schedule_id)


@router.get("/{schedule_id}", response_model=StudentSchedule)
def get_schedule_by_id(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific schedule by ID"""
    schedule = student_schedule.get(db, id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Planning non trouvé")

    # Add student name
    schedule.etudiant_nom = f"{schedule.etudiant.prenom} {schedule.etudiant.nom}"

    return schedule

# CREATE a new schedule (admin/manual)


@router.post("/", response_model=StudentSchedule)
def create_student_schedule(
    schedule_in: StudentScheduleCreate,
    db: Session = Depends(get_db)
):
    db_schedule = student_schedule.create_with_validation(
        db, obj_in=schedule_in)
    return db_schedule

# UPDATE a schedule (main fields)


@router.put("/{schedule_id}", response_model=StudentSchedule)
def update_student_schedule(
    schedule_id: str,
    update_in: StudentScheduleUpdate,
    db: Session = Depends(get_db)
):
    db_schedule = student_schedule.get(db, id=schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    db_schedule = student_schedule.update_with_validation(
        db, db_obj=db_schedule, obj_in=update_in)
    return db_schedule

# DELETE a schedule (hard delete)


@router.delete("/{schedule_id}", response_model=MessageResponse)
def delete_student_schedule(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    """Delete a student schedule"""
    db_schedule = student_schedule.get(db, id=schedule_id)
    if not db_schedule:
        raise HTTPException(
            status_code=404, detail="Planning étudiant non trouvé")

    student_schedule.remove(db, id=schedule_id)
    return {"message": "Planning étudiant supprimé avec succès"}

# CREATE a new detail row (admin/manual)


@router.post("/{schedule_id}/detail", response_model=StudentScheduleDetail)
def create_schedule_detail(
    schedule_id: str,
    detail_in: StudentScheduleDetailCreate,
    db: Session = Depends(get_db)
):
    # Set the schedule_id from the URL parameter
    detail_in.schedule_id = schedule_id
    db_detail = student_schedule_detail.create_with_validation(
        db, obj_in=detail_in)
    return db_detail

# UPDATE a detail row


@router.put("/{schedule_id}/detail/{detail_id}", response_model=StudentScheduleDetail)
def update_schedule_detail(
    schedule_id: str,
    detail_id: str,
    detail_in: StudentScheduleDetailCreate,
    db: Session = Depends(get_db)
):
    db_detail = student_schedule_detail.get(db, id=detail_id)
    if not db_detail:
        raise HTTPException(status_code=404, detail="Détail non trouvé")

    # Ensure the detail belongs to the specified schedule
    if db_detail.schedule_id != schedule_id:
        raise HTTPException(
            status_code=400, detail="Détail n'appartient pas à ce planning")

    # Set the schedule_id from the URL parameter
    detail_in.schedule_id = schedule_id
    db_detail = student_schedule_detail.update_with_validation(
        db, db_obj=db_detail, obj_in=detail_in)
    return db_detail

# DELETE a detail row


@router.delete("/{schedule_id}/detail/{detail_id}", response_model=MessageResponse)
def delete_schedule_detail(
    schedule_id: str,
    detail_id: str,
    db: Session = Depends(get_db)
):
    db_detail = student_schedule_detail.get(db, id=detail_id)
    if not db_detail:
        raise HTTPException(status_code=404, detail="Détail non trouvé")

    # Ensure the detail belongs to the specified schedule
    if db_detail.schedule_id != schedule_id:
        raise HTTPException(
            status_code=400, detail="Détail n'appartient pas à ce planning")

    student_schedule_detail.remove(db, id=detail_id)
    return {"message": "Détail supprimé avec succès"}

# EXPORT a schedule to Excel


@router.get("/{schedule_id}/export")
def export_schedule_excel(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    schedule = student_schedule.get(db, id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    details = db.query(StudentScheduleDetail).filter_by(
        schedule_id=schedule_id).all()
    data = [
        {
            "Service": d.service_nom,
            "Ordre": d.ordre_service,
            "Début": d.date_debut,
            "Fin": d.date_fin,
            "Durée (jours)": d.duree_jours,
            "Statut": d.statut,
            "Notes": d.notes or ""
        } for d in details
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Planning")
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=planning_{schedule_id}.xlsx"}
    )

# EXPORT all schedules for a planning to Excel


@router.get("/planning/{planning_id}/export")
def export_planning_excel(
    planning_id: str,
    db: Session = Depends(get_db)
):
    schedules = student_schedule.get_by_planning(db, planning_id=planning_id)
    all_data = []
    for sched in schedules:
        details = db.query(StudentScheduleDetail).filter_by(
            schedule_id=sched.id).all()
        for d in details:
            all_data.append({
                "Étudiant": f"{sched.etudiant.prenom} {sched.etudiant.nom}",
                "Service": d.service_nom,
                "Ordre": d.ordre_service,
                "Début": d.date_debut,
                "Fin": d.date_fin,
                "Durée (jours)": d.duree_jours,
                "Statut": d.statut,
                "Notes": d.notes or ""
            })
    df = pd.DataFrame(all_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Plannings")
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=planning_{planning_id}.xlsx"}
    )


@router.post("/generate-from-rotations/{promotion_id}", response_model=MessageResponse)
def generate_student_schedules_from_rotations(
    promotion_id: str,
    db: Session = Depends(get_db)
):
    """Generate student schedules from existing rotations for a promotion"""
    try:
        from ...models import Planning, Rotation, Etudiant, Service, StudentSchedule as StudentScheduleModel
        from datetime import datetime
        from collections import defaultdict

        # Get the planning for this promotion
        planning = db.query(Planning).filter(
            Planning.promo_id == promotion_id).first()
        if not planning:
            raise HTTPException(
                status_code=404, detail="Aucun planning trouvé pour cette promotion")

        # Get all rotations for this planning
        rotations = db.query(Rotation).filter(
            Rotation.planning_id == planning.id).all()
        if not rotations:
            raise HTTPException(
                status_code=404, detail="Aucune rotation trouvée pour ce planning")

        # Group rotations by student
        rotations_by_student = defaultdict(list)
        for rotation in rotations:
            rotations_by_student[rotation.etudiant_id].append(rotation)

        # Calculate overall planning dates
        all_start_dates = [datetime.strptime(
            r.date_debut, "%Y-%m-%d") for r in rotations]
        all_end_dates = [datetime.strptime(
            r.date_fin, "%Y-%m-%d") for r in rotations]

        planning_start_date = min(all_start_dates).strftime("%Y-%m-%d")
        planning_end_date = max(all_end_dates).strftime("%Y-%m-%d")

        created_schedules = 0

        for etudiant_id, student_rotations in rotations_by_student.items():
            # Check if student schedule already exists for this planning
            existing_schedule = db.query(StudentScheduleModel).filter(
                StudentScheduleModel.etudiant_id == etudiant_id,
                StudentScheduleModel.planning_id == planning.id,
                StudentScheduleModel.is_active == True
            ).first()

            if existing_schedule:
                continue  # Skip if already exists

            # Sort rotations by order
            sorted_rotations = sorted(student_rotations, key=lambda r: r.ordre)

            # Convert rotations to the format expected by create_from_planning
            rotations_dict = []
            for rotation in sorted_rotations:
                # Get service name from the service table
                service_name = "Service"
                if rotation.service_id:
                    service = db.query(Service).filter(
                        Service.id == rotation.service_id).first()
                    if service:
                        service_name = service.nom

                rotations_dict.append({
                    'id': rotation.id,
                    'service_id': rotation.service_id,
                    'service_nom': service_name,
                    'ordre': rotation.ordre,
                    'date_debut': rotation.date_debut,
                    'date_fin': rotation.date_fin
                })

            # Use the existing create_from_planning method
            student_schedule.create_from_planning(
                db=db,
                planning_id=planning.id,
                etudiant_id=etudiant_id,
                rotations=rotations_dict,
                date_debut_planning=planning_start_date,
                date_fin_planning=planning_end_date
            )

            created_schedules += 1

        return {"message": f"Plannings individuels créés pour {created_schedules} étudiant(s)"}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a generic message
        print(f"Error in generate_student_schedules_from_rotations: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la génération des plannings: {str(e)}")
