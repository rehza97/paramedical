# Migration Guide: Monolithic to Modular Architecture

## Overview

This guide explains the migration from the monolithic `server.py` to the new modular architecture.

## File Structure Comparison

### Before (Monolithic)

```
backend/
├── server.py                     # Single file with all code (272 lines)
├── database.py                   # Database configuration
├── models.py                     # SQLAlchemy models
├── schemas.py                    # Pydantic schemas
├── requirements.txt
└── ...
```

### After (Modular)

```
backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app initialization
│   ├── database.py               # Database configuration
│   ├── models.py                 # SQLAlchemy models
│   ├── schemas.py                # Pydantic schemas
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   └── endpoints/            # API endpoints
│   │       ├── __init__.py
│   │       ├── promotions.py     # Promotion endpoints
│   │       ├── services.py       # Service endpoints
│   │       └── plannings.py      # Planning endpoints
│   └── crud/                     # Data access layer
│       ├── __init__.py
│       ├── base.py               # Base CRUD operations
│       ├── promotion.py          # Promotion CRUD
│       ├── service.py            # Service CRUD
│       ├── etudiant.py           # Student CRUD
│       ├── rotation.py           # Rotation CRUD
│       └── planning.py           # Planning CRUD
├── server_modular.py             # New modular server entry point
├── server.py                     # Original server (kept for compatibility)
└── requirements.txt
```

## Code Organization Improvements

### 1. Separation of Concerns

**Before:** All code in one file

- API endpoints
- Database operations
- Business logic
- Data validation

**After:** Clear separation

- **API Layer**: HTTP endpoints and request handling
- **CRUD Layer**: Database operations and business logic
- **Models**: Database schema definition
- **Schemas**: Request/response validation

### 2. Reusability

**Before:** Duplicate code for similar operations

```python
# Repeated patterns in server.py
db_promotion = Promotion(...)
db.add(db_promotion)
db.commit()
db.refresh(db_promotion)
```

**After:** Reusable base CRUD class

```python
# Base operations available for all entities
promotion.create(db=db, obj_in=promotion_data)
service.get(db=db, id=service_id)
```

### 3. Type Safety

**Before:** Limited type hints

```python
def create_promotion(promotion: PromotionCreate, db: Session = Depends(get_db)):
    # Implementation...
```

**After:** Full type safety throughout

```python
def create_with_students(
    self, db: Session, *, obj_in: PromotionCreate
) -> Promotion:
    # Implementation with full type hints...
```

## API Endpoint Changes

### URL Structure

**Before:**

```
POST /promotions
GET /promotions
GET /promotions/{id}
DELETE /promotions/{id}
```

**After:**

```
POST /api/promotions
GET /api/promotions
GET /api/promotions/{id}
DELETE /api/promotions/{id}
```

All endpoints now have the `/api` prefix for better organization.

### Response Consistency

**Before:** Mixed response formats

```python
return {"id": str(db_promotion.id), "message": "Promotion créée avec succès"}
return db_promotion  # Direct model return
```

**After:** Consistent response schemas

```python
return IdResponse(id=db_promotion.id, message="Promotion créée avec succès")
return Planning(...)  # Always using Pydantic schemas
```

## Running the Application

### Old Way

```bash
python server.py
```

### New Way (Options)

```bash
# Option 1: Use the modular server script
python server_modular.py

# Option 2: Use uvicorn directly (recommended for production)
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Database Operations

### Before: Direct SQLAlchemy in endpoints

```python
@app.post("/promotions/", response_model=dict)
def create_promotion(promotion: PromotionCreate, db: Session = Depends(get_db)):
    # Validation logic mixed with database operations
    if not promotion.etudiants or len(promotion.etudiants) == 0:
        raise HTTPException(...)

    # Direct database operations
    db_promotion = Promotion(...)
    db.add(db_promotion)
    # ... more database code
```

### After: Clean separation with CRUD layer

```python
@router.post("/", response_model=IdResponse)
def create_promotion(
    promotion_in: PromotionCreate,
    db: Session = Depends(get_db)
):
    """Create a new promotion with students"""
    db_promotion = promotion.create_with_students(db=db, obj_in=promotion_in)
    return {"id": db_promotion.id, "message": "Promotion créée avec succès"}
```

## Benefits of Migration

1. **Maintainability**: Easier to find and modify specific functionality
2. **Testability**: Each component can be tested independently
3. **Scalability**: Easy to add new features without affecting existing code
4. **Code Reuse**: Common operations are centralized
5. **Type Safety**: Better IDE support and fewer runtime errors
6. **Documentation**: Self-documenting code structure

## Backward Compatibility

- Original `server.py` is kept for compatibility
- Same database schema and operations
- Same API functionality (with `/api` prefix)
- Same response formats

## Migration Steps

1. **Test the new server**:

   ```bash
   python server_modular.py
   ```

2. **Verify endpoints work**:

   ```bash
   curl http://localhost:8001/api/health
   curl http://localhost:8001/api/promotions
   ```

3. **Update client applications** to use `/api` prefix

4. **Deploy the new version**

5. **Remove old files** when confident:
   - `server.py` (already moved to modular structure)
   - Root-level `database.py`, `models.py`, `schemas.py` (moved to `app/`)

## Troubleshooting

### Import Errors

Make sure you're in the backend directory when running:

```bash
cd backend
python server_modular.py
```

### Database Connection

The database configuration remains the same in `app/database.py`

### Alembic Migrations

Updated to work with the new structure:

```bash
alembic revision --autogenerate -m "Migration message"
alembic upgrade head
```

This modular architecture provides a solid foundation for future development and maintenance of the paramedical internship management system.
