from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Base schemas


class SpecialityBase(BaseModel):
    nom: str
    description: Optional[str] = None
    duree_annees: int = 3


class SpecialityCreate(SpecialityBase):
    pass


class Speciality(SpecialityBase):
    id: str
    date_creation: datetime

    class Config:
        from_attributes = True


class EtudiantBase(BaseModel):
    nom: str
    prenom: str


class EtudiantCreate(EtudiantBase):
    is_active: bool = True


class Etudiant(EtudiantBase):
    id: str
    promotion_id: str
    is_active: bool

    class Config:
        from_attributes = True


class PromotionBase(BaseModel):
    nom: str
    annee: int
    speciality_id: Optional[str] = None


class PromotionCreate(PromotionBase):
    etudiants: List[EtudiantCreate]


class Promotion(PromotionBase):
    id: str
    date_creation: datetime
    etudiants: List[Etudiant]
    speciality: Optional[Speciality] = None

    class Config:
        from_attributes = True

# PromotionYear schemas


class PromotionYearBase(BaseModel):
    promotion_id: str
    annee_niveau: int  # 1, 2, 3, 4, or 5
    annee_calendaire: int  # 2024, 2025, etc.
    nom: Optional[str] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    is_active: bool = True


class PromotionYearCreate(PromotionYearBase):
    pass


class PromotionYear(PromotionYearBase):
    id: str
    date_creation: datetime

    class Config:
        from_attributes = True


class ServiceBase(BaseModel):
    nom: str
    places_disponibles: int
    duree_stage_jours: int
    speciality_id: str


class ServiceCreate(ServiceBase):
    pass


class Service(ServiceBase):
    id: str
    date_creation: datetime

    class Config:
        from_attributes = True


class RotationBase(BaseModel):
    etudiant_id: str
    service_id: str
    date_debut: str
    date_fin: str
    ordre: int


class RotationCreate(RotationBase):
    pass


class RotationUpdate(BaseModel):
    etudiant_id: Optional[str] = None
    service_id: Optional[str] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    ordre: Optional[int] = None


class Rotation(RotationBase):
    id: str
    planning_id: str
    etudiant_nom: Optional[str] = None
    service_nom: Optional[str] = None

    class Config:
        from_attributes = True


class PlanningBase(BaseModel):
    promo_id: str
    promotion_year_id: Optional[str] = None
    annee_niveau: Optional[int] = None


class PlanningCreate(PlanningBase):
    pass


class Planning(PlanningBase):
    id: str
    date_creation: datetime
    promo_nom: Optional[str] = None
    rotations: List[Rotation]

    class Config:
        from_attributes = True

# Student Schedule schemas


class StudentScheduleDetailBase(BaseModel):
    service_id: str
    service_nom: str
    ordre_service: int
    date_debut: str
    date_fin: str
    duree_jours: int
    statut: str = "planifie"
    notes: Optional[str] = None


class StudentScheduleDetailCreate(StudentScheduleDetailBase):
    schedule_id: str
    rotation_id: str


class StudentScheduleDetail(StudentScheduleDetailBase):
    id: str
    schedule_id: str
    rotation_id: str
    date_debut_reelle: Optional[str] = None
    date_fin_reelle: Optional[str] = None
    modifications: Optional[str] = None

    class Config:
        from_attributes = True


class StudentScheduleBase(BaseModel):
    etudiant_id: str
    planning_id: str
    date_debut_planning: str
    date_fin_planning: str
    nb_services_total: int
    duree_totale_jours: int
    statut: str = "en_cours"


class StudentScheduleCreate(StudentScheduleBase):
    pass


class StudentSchedule(StudentScheduleBase):
    id: str
    date_creation: datetime
    date_modification: Optional[datetime] = None
    version: int
    is_active: bool
    nb_services_completes: int
    taux_occupation_moyen: int
    etudiant_nom: Optional[str] = None
    schedule_details: List[StudentScheduleDetail]

    class Config:
        from_attributes = True

# Response schemas


class MessageResponse(BaseModel):
    message: str


class IdResponse(BaseModel):
    id: str
    message: str


class PlanningResponse(BaseModel):
    message: str
    planning: Optional[Planning] = None
    plannings: Optional[List[Planning]] = None
    number_of_services: int
    number_of_students: int


class StudentPlanningResponse(BaseModel):
    etudiant_id: str
    rotations: List[Rotation]

# Advanced planning algorithm schemas


class AdvancedPlanningRequest(BaseModel):
    promo_id: str
    date_debut: str = "2025-01-01"


class ServiceOccupationStats(BaseModel):
    taux_occupation: float
    jours_actifs: int
    occupation_moyenne: float


class PlanningEfficiencyAnalysis(BaseModel):
    duree_totale_jours: int
    date_debut: str
    date_fin: str
    nb_rotations: int
    occupation_services: Dict[str, ServiceOccupationStats]


class PlanningValidationResult(BaseModel):
    is_valid: bool
    erreurs: List[str]


class AdvancedPlanningResponse(BaseModel):
    message: str
    planning: Planning
    efficiency_analysis: PlanningEfficiencyAnalysis
    validation_result: PlanningValidationResult

# Student Schedule specific schemas


class StudentScheduleSummary(BaseModel):
    """Summary view of a student's schedule"""
    id: str
    etudiant_id: str
    etudiant_nom: str
    etudiant_prenom: str
    planning_id: str
    date_debut_planning: str
    date_fin_planning: str
    nb_services_total: int
    nb_services_completes: int
    duree_totale_jours: int
    statut: str
    progression: float  # Percentage of completed services

    class Config:
        from_attributes = True


class StudentScheduleUpdate(BaseModel):
    """Schema for updating student schedule details"""
    statut: Optional[str] = None
    date_debut_reelle: Optional[str] = None
    date_fin_reelle: Optional[str] = None
    notes: Optional[str] = None


class StudentScheduleProgress(BaseModel):
    """Schema for tracking student progress"""
    etudiant_id: str
    etudiant_nom: str
    services_completes: List[str]
    services_en_cours: List[str]
    services_planifies: List[str]
    progression_globale: float
    prochaine_service: Optional[str] = None
    date_prochaine_service: Optional[str] = None

# Planning Settings Schemas


class PlanningSettingsBase(BaseModel):
    academic_year_start: str
    total_duration_months: int
    max_concurrent_students: int
    break_days_between_rotations: int
    is_active: bool = True


class PlanningSettingsCreate(PlanningSettingsBase):
    pass


class PlanningSettingsUpdate(BaseModel):
    academic_year_start: Optional[str] = None
    total_duration_months: Optional[int] = None
    max_concurrent_students: Optional[int] = None
    break_days_between_rotations: Optional[int] = None
    is_active: Optional[bool] = None


class PlanningSettings(PlanningSettingsBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
