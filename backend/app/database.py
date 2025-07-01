from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration - using English database name to avoid encoding issues
DATABASE_URL = os.environ.get(
    'DATABASE_URL', 
    'postgresql://postgres:123456789@localhost:5432/paramedical_internships'
)

# Create SQLAlchemy engine with proper encoding
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "options": "-c client_encoding=utf8"
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 