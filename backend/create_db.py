#!/usr/bin/env python3
"""
Database creation script
Creates the PostgreSQL database with proper encoding
"""

import os
import sys
from sqlalchemy import create_engine, text

def create_database():
    """Create the database with proper encoding"""
    print("🏥 Creating Paramedical Internships Database 🏥")
    
    # Base connection URL (without database name)
    base_url = "postgresql://postgres:123456789@localhost:5432/postgres"
    
    try:
        # Connect to default postgres database with autocommit
        engine = create_engine(base_url, isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'paramedical_internships'"))
            if not result.fetchone():
                # Create database using template0 to avoid locale issues
                conn.execute(text("CREATE DATABASE paramedical_internships TEMPLATE template0 ENCODING 'UTF8'"))
                print("✅ Database 'paramedical_internships' created successfully")
            else:
                print("✅ Database 'paramedical_internships' already exists")
        
        print("\n🎉 Database creation completed!")
        print("\nNext steps:")
        print("1. Run: python init_db.py")
        print("2. Start the server: python server.py")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print(f"\nError type: {type(e).__name__}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Verify postgres user has password '123456789'")
        print("3. Check if you have permission to create databases")
        sys.exit(1)

if __name__ == "__main__":
    create_database() 