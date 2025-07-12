from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid
from datetime import datetime


def generate_uuid():
    return str(uuid.uuid4())


# Association table for promotion-services (keeping for backward compatibility)
promotion_services = Table(
    'promotion_services', Base.metadata,
    Column('promotion_id', String(36), ForeignKey(
        'promotions.id', ondelete='CASCADE'), primary_key=True),
    Column('service_id', String(36), ForeignKey(
        'services.id', ondelete='CASCADE'), primary_key=True)
)

# New association table for promotion year-specific services
promotion_year_services = Table(
    'promotion_year_services', Base.metadata,
    Column('promotion_year_id', String(36), ForeignKey(
        'promotion_years.id', ondelete='CASCADE'), primary_key=True),
    Column('service_id', String(36), ForeignKey(
        'services.id', ondelete='CASCADE'), primary_key=True)
)


class Speciality(Base):
    __tablename__ = "specialities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    nom = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    duree_annees = Column(Integer, nullable=False,
                          default=3)  # 3, 4, or 5 years
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    promotions = relationship("Promotion", back_populates="speciality")
    services = relationship("Service", back_populates="speciality")


class Etudiant(Base):
    __tablename__ = "etudiants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    promotion_id = Column(String(36), ForeignKey(
        "promotions.id"), nullable=False)
    # Current year (1, 2, 3, 4, or 5)
    annee_courante = Column(Integer, nullable=False, default=1)
    # Whether this student is active (enabled for planning)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationship
    promotion = relationship("Promotion", back_populates="etudiants")
    rotations = relationship("Rotation", back_populates="etudiant")
    schedules = relationship("StudentSchedule", back_populates="etudiant")


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    nom = Column(String(200), nullable=False)
    annee = Column(Integer, nullable=False)  # Starting year (e.g., 2024)
    speciality_id = Column(String(36), ForeignKey(
        "specialities.id"), nullable=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    etudiants = relationship(
        "Etudiant", back_populates="promotion", cascade="all, delete-orphan")
    plannings = relationship(
        "Planning", back_populates="promotion", cascade="all, delete-orphan")
    services = relationship("Service", secondary=promotion_services,
                            back_populates="promotions")  # Keep for backward compatibility
    speciality = relationship("Speciality", back_populates="promotions")
    promotion_years = relationship(
        "PromotionYear", back_populates="promotion", cascade="all, delete-orphan")


class PromotionYear(Base):
    """Represents a specific year of a promotion (e.g., 1st year, 2nd year, etc.)"""
    __tablename__ = "promotion_years"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    promotion_id = Column(String(36), ForeignKey(
        "promotions.id"), nullable=False)
    # Year level: 1, 2, 3, 4, or 5
    annee_niveau = Column(Integer, nullable=False)
    # Calendar year (e.g., 2024, 2025)
    annee_calendaire = Column(Integer, nullable=False)
    # Optional name like "1ère année", "2ème année"
    nom = Column(String(200), nullable=True)
    date_debut = Column(String(10), nullable=True)  # Academic year start date
    date_fin = Column(String(10), nullable=True)    # Academic year end date
    # Whether this year is currently active
    is_active = Column(Boolean, default=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    promotion = relationship("Promotion", back_populates="promotion_years")
    services = relationship(
        "Service", secondary=promotion_year_services, back_populates="promotion_years")
    plannings = relationship(
        "Planning", back_populates="promotion_year", cascade="all, delete-orphan")


class Service(Base):
    __tablename__ = "services"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    nom = Column(String(200), nullable=False, unique=True)
    places_disponibles = Column(Integer, nullable=False)
    duree_stage_jours = Column(Integer, nullable=False)
    speciality_id = Column(String(36), ForeignKey(
        "specialities.id"), nullable=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    speciality = relationship("Speciality", back_populates="services")
    rotations = relationship("Rotation", back_populates="service")
    promotions = relationship("Promotion", secondary=promotion_services,
                              back_populates="services")  # Keep for backward compatibility
    promotion_years = relationship(
        "PromotionYear", secondary=promotion_year_services, back_populates="services")


class Rotation(Base):
    __tablename__ = "rotations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(String(36), ForeignKey(
        "etudiants.id"), nullable=False)
    service_id = Column(String(36), ForeignKey("services.id"), nullable=False)
    date_debut = Column(String(10), nullable=False)  # Stored as YYYY-MM-DD
    date_fin = Column(String(10), nullable=False)    # Stored as YYYY-MM-DD
    ordre = Column(Integer, nullable=False)
    planning_id = Column(String(36), ForeignKey(
        "plannings.id"), nullable=False)
    promotion_year_id = Column(String(36), ForeignKey(
        "promotion_years.id"), nullable=False)  # NEW

    # Relationships
    etudiant = relationship("Etudiant", back_populates="rotations")
    service = relationship("Service", back_populates="rotations")
    planning = relationship("Planning", back_populates="rotations")
    # Optionally, add:
    # promotion_year = relationship("PromotionYear")


class Planning(Base):
    __tablename__ = "plannings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    promo_id = Column(String(36), ForeignKey("promotions.id"), nullable=False)
    promotion_year_id = Column(String(36), ForeignKey(
        "promotion_years.id"), nullable=True)  # New: Link to specific year
    # Year level for this planning (1, 2, 3, etc.)
    annee_niveau = Column(Integer, nullable=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    promotion = relationship("Promotion", back_populates="plannings")
    promotion_year = relationship("PromotionYear", back_populates="plannings")
    rotations = relationship(
        "Rotation", back_populates="planning", cascade="all, delete-orphan")
    student_schedules = relationship(
        "StudentSchedule", back_populates="planning", cascade="all, delete-orphan")


class PlanningSettings(Base):
    __tablename__ = "planning_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    academic_year_start = Column(
        String, nullable=False, default="2025-01-01")  # Default start date
    total_duration_months = Column(
        Integer, nullable=False, default=6)  # Total duration in months
    max_concurrent_students = Column(
        Integer, nullable=False, default=2)  # Max students per service
    break_days_between_rotations = Column(
        Integer, nullable=False, default=2)  # Days between rotations
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)


class StudentSchedule(Base):
    """Table to track individual student internship schedules"""
    __tablename__ = "student_schedules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(String(36), ForeignKey(
        "etudiants.id"), nullable=False)
    planning_id = Column(String(36), ForeignKey(
        "plannings.id"), nullable=False)

    # Schedule metadata
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    version = Column(Integer, default=1)  # For tracking schedule versions
    # To mark current vs historical schedules
    is_active = Column(Boolean, default=True)

    # Schedule details
    # Overall planning start date
    date_debut_planning = Column(String(10), nullable=False)
    # Overall planning end date
    date_fin_planning = Column(String(10), nullable=False)
    # Total number of services in schedule
    nb_services_total = Column(Integer, nullable=False)
    # Number of completed services
    nb_services_completes = Column(Integer, default=0)

    # Performance metrics
    # Total duration in days
    duree_totale_jours = Column(Integer, nullable=False)
    # Average occupation rate (%)
    taux_occupation_moyen = Column(Integer, default=0)

    # Status tracking
    # en_cours, termine, suspendu, annule
    statut = Column(String(50), default="en_cours")

    # Relationships
    etudiant = relationship("Etudiant", back_populates="schedules")
    planning = relationship("Planning", back_populates="student_schedules")
    schedule_details = relationship(
        "StudentScheduleDetail", back_populates="schedule", cascade="all, delete-orphan")


class StudentScheduleDetail(Base):
    """Detailed breakdown of each service in a student's schedule"""
    __tablename__ = "student_schedule_details"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    schedule_id = Column(String(36), ForeignKey(
        "student_schedules.id"), nullable=False)
    rotation_id = Column(String(36), ForeignKey(
        "rotations.id"), nullable=False)

    # Service details
    service_id = Column(String(36), ForeignKey("services.id"), nullable=False)
    service_nom = Column(String(200), nullable=False)
    # Order in the student's schedule
    ordre_service = Column(Integer, nullable=False)

    # Timing
    date_debut = Column(String(10), nullable=False)
    date_fin = Column(String(10), nullable=False)
    duree_jours = Column(Integer, nullable=False)

    # Status tracking
    # planifie, en_cours, termine, annule
    statut = Column(String(50), default="planifie")
    # Actual start date if different
    date_debut_reelle = Column(String(10), nullable=True)
    # Actual end date if different
    date_fin_reelle = Column(String(10), nullable=True)

    # Notes and modifications
    notes = Column(Text, nullable=True)
    modifications = Column(Text, nullable=True)  # JSON string of modifications

    # Relationships
    schedule = relationship(
        "StudentSchedule", back_populates="schedule_details")
    rotation = relationship("Rotation")
    service = relationship("Service")
