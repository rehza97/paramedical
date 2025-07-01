from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io
import pandas as pd

from ...database import get_db
from ...crud import student_schedule
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
    schedule = student_schedule.get_active_by_etudiant(db, etudiant_id=etudiant_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Aucun planning actif trouvé")
    
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
    db_schedule = student_schedule.create(db, obj_in=schedule_in)
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
    db_schedule = student_schedule.update(db, db_obj=db_schedule, obj_in=update_in)
    return db_schedule

# DELETE a schedule (hard delete)
@router.delete("/{schedule_id}", response_model=MessageResponse)
def delete_student_schedule(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    db_schedule = student_schedule.get(db, id=schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    student_schedule.remove(db, id=schedule_id)
    return {"message": "Planning supprimé avec succès"}

# CREATE a new detail row (admin/manual)
@router.post("/{schedule_id}/detail", response_model=StudentScheduleDetail)
def create_schedule_detail(
    schedule_id: str,
    detail_in: StudentScheduleDetailCreate,
    db: Session = Depends(get_db)
):
    db_detail = StudentScheduleDetail(
        id=None,
        schedule_id=schedule_id,
        rotation_id=None,
        service_id=detail_in.service_id,
        service_nom=detail_in.service_nom,
        ordre_service=detail_in.ordre_service,
        date_debut=detail_in.date_debut,
        date_fin=detail_in.date_fin,
        duree_jours=detail_in.duree_jours,
        statut=detail_in.statut,
        notes=detail_in.notes
    )
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    return db_detail

# UPDATE a detail row
@router.put("/{schedule_id}/detail/{detail_id}", response_model=StudentScheduleDetail)
def update_schedule_detail(
    schedule_id: str,
    detail_id: str,
    detail_in: StudentScheduleDetailCreate,
    db: Session = Depends(get_db)
):
    db_detail = db.query(StudentScheduleDetail).filter_by(id=detail_id, schedule_id=schedule_id).first()
    if not db_detail:
        raise HTTPException(status_code=404, detail="Détail non trouvé")
    for field, value in detail_in.dict(exclude_unset=True).items():
        setattr(db_detail, field, value)
    db.commit()
    db.refresh(db_detail)
    return db_detail

# DELETE a detail row
@router.delete("/{schedule_id}/detail/{detail_id}", response_model=MessageResponse)
def delete_schedule_detail(
    schedule_id: str,
    detail_id: str,
    db: Session = Depends(get_db)
):
    db_detail = db.query(StudentScheduleDetail).filter_by(id=detail_id, schedule_id=schedule_id).first()
    if not db_detail:
        raise HTTPException(status_code=404, detail="Détail non trouvé")
    db.delete(db_detail)
    db.commit()
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
    details = db.query(StudentScheduleDetail).filter_by(schedule_id=schedule_id).all()
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
        headers={"Content-Disposition": f"attachment; filename=planning_{schedule_id}.xlsx"}
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
        details = db.query(StudentScheduleDetail).filter_by(schedule_id=sched.id).all()
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
        headers={"Content-Disposition": f"attachment; filename=planning_{planning_id}.xlsx"}
    ) 