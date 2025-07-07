#!/usr/bin/env python3
"""
Modular FastAPI server for Stages Paramédicaux
Uses the new modular structure with organized CRUD operations
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001) 
 
 
 