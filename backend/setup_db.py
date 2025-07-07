#!/usr/bin/env python3
"""
Database setup script for Stages Paramédicaux
This script initializes the PostgreSQL database and creates all necessary tables.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from app.database import DATABASE_URL, engine
from app import models


def create_database():
    """Create the database if it doesn't exist"""
    # Extract database name from URL
    db_name = DATABASE_URL.split('/')[-1]
    base_url = '/'.join(DATABASE_URL.split('/')[:-1])

    # Connect to PostgreSQL server (without specifying database), with AUTOCOMMIT
    engine_without_db = create_engine(
        base_url + '/postgres', isolation_level="AUTOCOMMIT")

    try:
        with engine_without_db.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            if not result.fetchone():
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Database '{db_name}' created successfully")
            else:
                print(f"✅ Database '{db_name}' already exists")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

    return True


def create_tables():
    """Create all tables"""
    try:
        # Create all tables
        models.Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def main():
    """Main setup function"""
    print("🏥 Setting up Stages Paramédicaux Database 🏥")
    print(f"Database URL: {DATABASE_URL}")

    # Create database
    if not create_database():
        print("❌ Failed to create database")
        sys.exit(1)

    # Create tables
    if not create_tables():
        print("❌ Failed to create tables")
        sys.exit(1)

    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the backend server: python server_modular.py")
    print("2. Run tests: python backend_test.py")
    print("3. Start the frontend: cd frontend && npm start")


if __name__ == "__main__":
    main()
