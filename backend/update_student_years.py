#!/usr/bin/env python3
"""
Script to update student annee_courante values to distribute students across years
"""

from app.crud.etudiant import etudiant
from app.models import Etudiant, Promotion
from app.database import SessionLocal
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def update_student_years():
    """Update student annee_courante to distribute them across years"""
    db = SessionLocal()
    try:
        # Get all students from the promotion
        promotion_id = "a6156fc0-a52a-45aa-bb10-e95a0e258d8e"  # Your promotion ID
        students = db.query(Etudiant).filter(
            Etudiant.promotion_id == promotion_id,
            Etudiant.is_active == True
        ).all()

        if not students:
            print("❌ No active students found in the promotion")
            return

        print(f"✅ Found {len(students)} active students")

        # Distribute students across years (1, 2, 3)
        students_per_year = len(students) // 3
        remainder = len(students) % 3

        year_1_count = students_per_year + (1 if remainder > 0 else 0)
        year_2_count = students_per_year + (1 if remainder > 1 else 0)
        year_3_count = students_per_year

        print(f"📊 Distribution plan:")
        print(f"   - Year 1: {year_1_count} students")
        print(f"   - Year 2: {year_2_count} students")
        print(f"   - Year 3: {year_3_count} students")

        # Update students
        for i, student in enumerate(students):
            if i < year_1_count:
                new_year = 1
            elif i < year_1_count + year_2_count:
                new_year = 2
            else:
                new_year = 3

            student.annee_courante = new_year
            print(f"   - {student.nom} {student.prenom}: Year {new_year}")

        db.commit()
        print("✅ Successfully updated student years!")

        # Verify the distribution
        year_1_students = db.query(Etudiant).filter(
            Etudiant.promotion_id == promotion_id,
            Etudiant.is_active == True,
            Etudiant.annee_courante == 1
        ).count()

        year_2_students = db.query(Etudiant).filter(
            Etudiant.promotion_id == promotion_id,
            Etudiant.is_active == True,
            Etudiant.annee_courante == 2
        ).count()

        year_3_students = db.query(Etudiant).filter(
            Etudiant.promotion_id == promotion_id,
            Etudiant.is_active == True,
            Etudiant.annee_courante == 3
        ).count()

        print(f"\n📋 Final distribution:")
        print(f"   - Year 1: {year_1_students} students")
        print(f"   - Year 2: {year_2_students} students")
        print(f"   - Year 3: {year_3_students} students")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    update_student_years()
