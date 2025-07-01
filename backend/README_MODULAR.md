# Stages Paramédicaux - Modular Backend Architecture

## Overview

This is the modularized version of the Stages Paramédicaux backend, organized following FastAPI best practices with clear separation of concerns.

## Project Structure

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
│       ├── planning.py           # Planning CRUD
│       └── advanced_planning.py  # Advanced planning algorithm
├── server_modular.py             # New modular server entry point
├── server.py                     # Original monolithic server (kept for compatibility)
├── alembic/                      # Database migrations
├── alembic.ini                   # Alembic configuration
└── requirements.txt              # Python dependencies
```

## Architecture Layers

### 1. Models Layer (`app/models.py`)

- SQLAlchemy ORM models
- Database table definitions
- Relationships between entities

### 2. Schemas Layer (`app/schemas.py`)

- Pydantic models for request/response validation
- Data serialization/deserialization
- Type hints and validation rules

### 3. CRUD Layer (`app/crud/`)

- Data access operations
- Business logic for database interactions
- Reusable database operations

### 4. API Layer (`app/api/endpoints/`)

- HTTP endpoints
- Request/response handling
- Input validation and error handling

### 5. Database Layer (`app/database.py`)

- Database connection configuration
- Session management
- Connection dependency injection

## Key Features of Modular Architecture

### Base CRUD Class

The `CRUDBase` class provides common operations:

- `get()` - Get single record by ID
- `get_multi()` - Get multiple records with pagination
- `create()` - Create new record
- `update()` - Update existing record
- `remove()` - Delete record

### Specialized CRUD Operations

Each entity has specialized operations:

**Promotions:**

- `create_with_students()` - Create promotion with students
- `get_with_students()` - Get promotion with all students
- `delete_with_cascade()` - Delete with all related data

**Services:**

- `create_with_validation()` - Create with business rules validation
- `update_with_validation()` - Update with validation

**Planning:**

- `generate_planning()` - Generate internship schedule
- `get_student_planning()` - Get planning for specific student

**Advanced Planning:**

- `generate_advanced_planning()` - Intelligent load balancing algorithm
- `analyze_efficiency()` - Efficiency analysis with occupation rates
- `validate_planning()` - Comprehensive planning validation

## Running the Modular Server

### Option 1: Use the new modular server

```bash
python server_modular.py
```

### Option 2: Use uvicorn directly

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

All endpoints are now organized under `/api` prefix:

### Promotions (`/api/promotions`)

- `POST /` - Create promotion with students
- `GET /` - List all promotions
- `GET /{promotion_id}` - Get specific promotion
- `DELETE /{promotion_id}` - Delete promotion

### Services (`/api/services`)

- `POST /` - Create service
- `GET /` - List all services
- `GET /{service_id}` - Get specific service
- `PUT /{service_id}` - Update service
- `DELETE /{service_id}` - Delete service

### Plannings (`/api/plannings`)

- `POST /generer/{promo_id}` - Generate basic planning
- `POST /generer-avance/{promo_id}` - **NEW** Generate advanced planning with AI
- `POST /analyser-efficacite/{promo_id}` - **NEW** Analyze planning efficiency
- `POST /valider/{promo_id}` - **NEW** Validate planning for errors
- `GET /{promo_id}` - Get planning for promotion
- `GET /etudiant/{promo_id}/{etudiant_id}` - Get student planning

### Health Check

- `GET /api/health` - Service health status

## Advanced Planning Algorithm Features

### 🧠 **Intelligent Load Balancing**

The advanced algorithm uses a sophisticated scoring system:

- **Availability Score (40%)**: Immediate service availability
- **Capacity Score (25%)**: Total service capacity
- **Urgency Score (25%)**: Priority for bottleneck services
- **Duration Score (10%)**: Preference for longer internships

### 📊 **Efficiency Analysis**

Provides detailed metrics:

- Total planning duration
- Service occupation rates
- Average students per service
- Active days per service

### ✅ **Comprehensive Validation**

Checks for:

- Capacity overruns by service and date
- Missing service assignments per student
- Scheduling conflicts
- Resource constraints

### 🎯 **Algorithm Benefits**

- **Optimal Resource Utilization**: Maximizes service capacity usage
- **Flexible Scheduling**: Adapts to varying service constraints
- **Conflict Resolution**: Automatically handles scheduling conflicts
- **Performance Metrics**: Provides actionable insights

## Benefits of Modular Architecture

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Reusability**: CRUD operations can be reused across endpoints
3. **Testability**: Each component can be tested independently
4. **Maintainability**: Changes are isolated to specific modules
5. **Scalability**: Easy to add new features without affecting existing code
6. **Type Safety**: Full type hints throughout the application
7. **Advanced Algorithms**: Sophisticated planning capabilities

## Migration from Monolithic

The original `server.py` is kept for backward compatibility. To migrate:

1. Test the new modular server: `python server_modular.py`
2. Verify all endpoints work correctly
3. Update deployment scripts to use `server_modular.py`
4. Remove `server.py` when confident in the new structure

## Database Operations

The modular structure maintains the same database schema and operations:

- PostgreSQL with SQLAlchemy ORM
- Alembic for migrations
- Proper relationship handling
- Transaction management

## Development Workflow

1. **Adding new endpoints**: Create in `app/api/endpoints/`
2. **Adding business logic**: Extend CRUD classes in `app/crud/`
3. **Database changes**: Update models and create migrations
4. **Schema changes**: Update Pydantic schemas in `app/schemas.py`
5. **Advanced algorithms**: Extend `app/crud/advanced_planning.py`

## Testing

Each layer can be tested independently:

- Unit tests for CRUD operations
- Integration tests for API endpoints
- Algorithm tests for planning logic
- Database tests with test fixtures

## Example Usage

### Generate Advanced Planning

```bash
curl -X POST "http://localhost:8001/api/plannings/generer-avance/PROMO_ID?date_debut=2025-01-01"
```

### Analyze Planning Efficiency

```bash
curl -X POST "http://localhost:8001/api/plannings/analyser-efficacite/PROMO_ID"
```

### Validate Planning

```bash
curl -X POST "http://localhost:8001/api/plannings/valider/PROMO_ID"
```

This modular architecture provides a solid foundation for maintaining and extending the paramedical internship management system with advanced AI-powered planning capabilities.
