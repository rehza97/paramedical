#!/usr/bin/env python3
"""
Quick database initialization script
This script creates the database and tables without using Alembic
"""

import os
import sys
from sqlalchemy import create_engine, text
from database import DATABASE_URL, engine
import models

def main():
    """Initialize the database"""
    print("🏥 Initializing Stages Paramédicaux Database 🏥")
    
    try:
        # Test connection first
        print("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
        
        # Create all tables
        print("Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        print("\n🎉 Database initialization completed!")
        print("\nYou can now:")
        print("1. Start the server: python server.py")
        print("2. Run tests: python backend_test.py")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print(f"\nError type: {type(e).__name__}")
        print(f"\nMake sure PostgreSQL is running and accessible with:")
        print(f"URL: {DATABASE_URL}")
        
        # Provide specific troubleshooting steps
        print("\nTroubleshooting steps:")
        print("1. Ensure PostgreSQL is installed and running")
        print("2. Check if the postgres user exists and has password '123456789'")
        print("3. Verify the database 'stages_paramedicaux' exists or can be created")
        print("4. Check if port 5432 is available")
        
        sys.exit(1)

if __name__ == "__main__":
    main() 
"""
Quick database initialization script
This script creates the database and tables without using Alembic
"""

import os
import sys
from sqlalchemy import create_engine, text
from database import DATABASE_URL, engine
import models

def main():
    """Initialize the database"""
    print("🏥 Initializing Stages Paramédicaux Database 🏥")
    
    try:
        # Test connection first
        print("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
        
        # Create all tables
        print("Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        print("\n🎉 Database initialization completed!")
        print("\nYou can now:")
        print("1. Start the server: python server.py")
        print("2. Run tests: python backend_test.py")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print(f"\nError type: {type(e).__name__}")
        print(f"\nMake sure PostgreSQL is running and accessible with:")
        print(f"URL: {DATABASE_URL}")
        
        # Provide specific troubleshooting steps
        print("\nTroubleshooting steps:")
        print("1. Ensure PostgreSQL is installed and running")
        print("2. Check if the postgres user exists and has password '123456789'")
        print("3. Verify the database 'stages_paramedicaux' exists or can be created")
        print("4. Check if port 5432 is available")
        
        sys.exit(1)

if __name__ == "__main__":
    main() 
 
 