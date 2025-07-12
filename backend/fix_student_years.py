#!/usr/bin/env python3
"""
Simple script to update student annee_courante values
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    # Database connection
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/paramedical_db"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def update_student_years():
        """Update student annee_courante to distribute them across years"""
        db = SessionLocal()
        try:
            # Get all students from the promotion
            promotion_id = "a6156fc0-a52a-45aa-bb10-e95a0e258d8e"

            # Count current students
            result = db.execute(text("""
                SELECT COUNT(*) as count 
                FROM etudiants 
                WHERE promotion_id = :promotion_id AND is_active = true
            """), {"promotion_id": promotion_id})
            total_students = result.fetchone()[0]

            if total_students == 0:
                print("❌ No active students found in the promotion")
                return

            print(f"✅ Found {total_students} active students")

            # Distribute students across years (1, 2, 3)
            students_per_year = total_students // 3
            remainder = total_students % 3

            year_1_count = students_per_year + (1 if remainder > 0 else 0)
            year_2_count = students_per_year + (1 if remainder > 1 else 0)
            year_3_count = students_per_year

            print(f"📊 Distribution plan:")
            print(f"   - Year 1: {year_1_count} students")
            print(f"   - Year 2: {year_2_count} students")
            print(f"   - Year 3: {year_3_count} students")

            # Get all students ordered by name
            result = db.execute(text("""
                SELECT id, nom, prenom, annee_courante 
                FROM etudiants 
                WHERE promotion_id = :promotion_id AND is_active = true
                ORDER BY nom, prenom
            """), {"promotion_id": promotion_id})
            students = result.fetchall()

            # Update students
            for i, student in enumerate(students):
                if i < year_1_count:
                    new_year = 1
                elif i < year_1_count + year_2_count:
                    new_year = 2
                else:
                    new_year = 3

                db.execute(text("""
                    UPDATE etudiants 
                    SET annee_courante = :new_year 
                    WHERE id = :student_id
                """), {"new_year": new_year, "student_id": student[0]})

                print(f"   - {student[1]} {student[2]}: Year {new_year}")

            db.commit()
            print("✅ Successfully updated student years!")

            # Verify the distribution
            for year in [1, 2, 3]:
                result = db.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM etudiants 
                    WHERE promotion_id = :promotion_id AND is_active = true AND annee_courante = :year
                """), {"promotion_id": promotion_id, "year": year})
                count = result.fetchone()[0]
                print(f"   - Year {year}: {count} students")

        except Exception as e:
            print(f"❌ Error: {e}")
            db.rollback()
        finally:
            db.close()

    if __name__ == "__main__":
        update_student_years()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have the required dependencies installed:")
    print("pip install sqlalchemy psycopg2-binary")
except Exception as e:
    print(f"❌ Error: {e}")
