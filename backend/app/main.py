from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models import Base
from .api import api_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Stages Paramédicaux API",
    description="API for managing paramedical internships",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "stages-paramedicaux-api"}

# Include API router
app.include_router(api_router, prefix="/api") 
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models import Base
from .api import api_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Stages Paramédicaux API",
    description="API for managing paramedical internships",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "stages-paramedicaux-api"}

# Include API router
app.include_router(api_router, prefix="/api") 
 
 