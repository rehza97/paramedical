# 🏥 Stages Paramédicaux - Complete System Documentation

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [API Documentation](#api-documentation)
6. [Frontend Features](#frontend-features)
7. [Installation & Setup](#installation--setup)
8. [Usage Guide](#usage-guide)
9. [Development](#development)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)

## 🎯 System Overview

**Stages Paramédicaux** is a comprehensive internship management system designed for paramedical education institutions. The system manages student cohorts, hospital departments, and internship scheduling with advanced planning algorithms.

### Key Features

- **Student Management**: Manage student cohorts and individual student records
- **Service Management**: Configure hospital departments and their capacities
- **Advanced Planning**: Intelligent internship scheduling with optimization algorithms
- **Speciality Management**: Organize students by medical specialities
- **Multi-year Support**: Handle different academic years within promotions
- **Progress Tracking**: Monitor student internship progress and completion
- **Excel Export**: Export planning data for external use
- **Real-time Updates**: Live dashboard with current system status

### Core Entities

- **Promotions**: Student cohorts (e.g., "Promotion 2024")
- **Specialities**: Medical specialities (e.g., "Infirmier", "Kinésithérapeute")
- **Services**: Hospital departments (e.g., "Cardiologie", "Urgences")
- **Students**: Individual student records with progress tracking
- **Plannings**: Internship schedules for entire promotions
- **Rotations**: Individual student assignments to services

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │   React     │ │  Tailwind   │ │  Radix UI   │         │
│  │   Router    │ │    CSS      │ │ Components  │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │  FastAPI    │ │   CORS      │ │  Pydantic   │         │
│  │   Server    │ │ Middleware  │ │ Validation  │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │   CRUD      │ │  Planning   │ │  Advanced   │         │
│  │ Operations  │ │ Algorithms  │ │  Scheduling │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Data Layer                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │ SQLAlchemy  │ │ PostgreSQL  │ │  Alembic    │         │
│  │    ORM      │ │  Database   │ │ Migrations  │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/          # API route handlers
│   │   │   ├── promotions.py
│   │   │   ├── services.py
│   │   │   ├── plannings.py
│   │   │   ├── student_schedules.py
│   │   │   ├── specialities.py
│   │   │   └── promotion_years.py
│   │   └── planning_settings.py
│   ├── crud/                   # Database operations
│   │   ├── base.py
│   │   ├── promotion.py
│   │   ├── service.py
│   │   ├── planning.py
│   │   ├── advanced_planning.py
│   │   └── student_schedule.py
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database configuration
│   └── main.py                 # FastAPI application
├── alembic/                    # Database migrations
├── requirements.txt
└── server.py                   # Server entry point
```

#### Frontend Structure

```
frontend/
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── ui/                # Radix UI components
│   │   ├── Table.js
│   │   ├── Modal.js
│   │   └── FormInput.js
│   ├── pages/                  # Main application pages
│   │   ├── DashboardPage.js
│   │   ├── StudentsPage.js
│   │   ├── PlanningPage.js
│   │   ├── SettingsPage.js
│   │   └── AdvancedPlanningsPage.js
│   ├── services/               # API communication
│   │   └── api.js
│   ├── contexts/               # React contexts
│   │   └── MessageContext.js
│   └── App.js                  # Main application component
├── public/
└── package.json
```

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI 0.110.1
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Testing**: pytest
- **Code Quality**: black, isort, flake8, mypy

### Frontend

- **Framework**: React 19.0.0
- **Routing**: React Router DOM 7.6.3
- **Styling**: Tailwind CSS 3.4.17
- **UI Components**: Radix UI
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Build Tool**: Create React App

### Development Tools

- **Version Control**: Git
- **Package Management**: npm/yarn (frontend), pip (backend)
- **Database**: PostgreSQL
- **API Documentation**: Swagger UI (FastAPI auto-generated)

## 📊 Database Schema

### Core Tables

#### 1. Specialities (`specialities`)

```sql
- id (UUID, Primary Key)
- nom (String, Unique) - Speciality name
- description (Text) - Speciality description
- duree_annees (Integer) - Duration in years (3, 4, or 5)
- date_creation (DateTime)
```

#### 2. Promotions (`promotions`)

```sql
- id (UUID, Primary Key)
- nom (String) - Promotion name
- annee (Integer) - Starting year
- speciality_id (UUID, Foreign Key) - Link to speciality
- date_creation (DateTime)
```

#### 3. Promotion Years (`promotion_years`)

```sql
- id (UUID, Primary Key)
- promotion_id (UUID, Foreign Key)
- annee_niveau (Integer) - Year level (1, 2, 3, 4, 5)
- annee_calendaire (Integer) - Calendar year
- nom (String) - Optional name
- date_debut (String) - Academic year start
- date_fin (String) - Academic year end
- is_active (Boolean)
- date_creation (DateTime)
```

#### 4. Students (`etudiants`)

```sql
- id (UUID, Primary Key)
- nom (String) - Last name
- prenom (String) - First name
- promotion_id (UUID, Foreign Key)
- annee_courante (Integer) - Current year (1-5)
- is_active (Boolean) - Whether student is active
```

#### 5. Services (`services`)

```sql
- id (UUID, Primary Key)
- nom (String, Unique) - Service name
- places_disponibles (Integer) - Available spots
- duree_stage_jours (Integer) - Internship duration in days
- speciality_id (UUID, Foreign Key)
- date_creation (DateTime)
```

#### 6. Plannings (`plannings`)

```sql
- id (UUID, Primary Key)
- promo_id (UUID, Foreign Key)
- promotion_year_id (UUID, Foreign Key)
- annee_niveau (Integer) - Year level for this planning
- date_creation (DateTime)
```

#### 7. Rotations (`rotations`)

```sql
- id (UUID, Primary Key)
- etudiant_id (UUID, Foreign Key)
- service_id (UUID, Foreign Key)
- planning_id (UUID, Foreign Key)
- date_debut (String) - Start date (YYYY-MM-DD)
- date_fin (String) - End date (YYYY-MM-DD)
- ordre (Integer) - Rotation order
```

#### 8. Student Schedules (`student_schedules`)

```sql
- id (UUID, Primary Key)
- etudiant_id (UUID, Foreign Key)
- planning_id (UUID, Foreign Key)
- date_debut_planning (String)
- date_fin_planning (String)
- nb_services_total (Integer)
- nb_services_completes (Integer)
- duree_totale_jours (Integer)
- taux_occupation_moyen (Integer)
- statut (String) - en_cours, termine, suspendu, annule
- version (Integer)
- is_active (Boolean)
```

#### 9. Student Schedule Details (`student_schedule_details`)

```sql
- id (UUID, Primary Key)
- schedule_id (UUID, Foreign Key)
- rotation_id (UUID, Foreign Key)
- service_id (UUID, Foreign Key)
- service_nom (String)
- ordre_service (Integer)
- date_debut (String)
- date_fin (String)
- duree_jours (Integer)
- statut (String) - planifie, en_cours, termine, annule
- date_debut_reelle (String)
- date_fin_reelle (String)
- notes (Text)
- modifications (Text) - JSON string
```

#### 10. Planning Settings (`planning_settings`)

```sql
- id (UUID, Primary Key)
- academic_year_start (String)
- total_duration_months (Integer)
- max_concurrent_students (Integer)
- break_days_between_rotations (Integer)
- is_active (Boolean)
- created_at (DateTime)
- updated_at (DateTime)
```

### Association Tables

#### Promotion Services (`promotion_services`)

```sql
- promotion_id (UUID, Foreign Key)
- service_id (UUID, Foreign Key)
```

#### Promotion Year Services (`promotion_year_services`)

```sql
- promotion_year_id (UUID, Foreign Key)
- service_id (UUID, Foreign Key)
```

## 🔌 API Documentation

### Base URL

```
http://localhost:8001/api
```

### Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

### Endpoints

#### Health Check

- `GET /health` - Service status

#### Specialities

- `GET /specialities` - List all specialities
- `POST /specialities` - Create new speciality
- `GET /specialities/{id}` - Get specific speciality
- `PUT /specialities/{id}` - Update speciality
- `DELETE /specialities/{id}` - Delete speciality

#### Promotions

- `GET /promotions` - List all promotions
- `POST /promotions` - Create new promotion
- `GET /promotions/{id}` - Get specific promotion
- `PUT /promotions/{id}` - Update promotion
- `DELETE /promotions/{id}` - Delete promotion

#### Promotion Years

- `GET /promotion-years` - List all promotion years
- `POST /promotion-years` - Create new promotion year
- `GET /promotion-years/{id}` - Get specific promotion year
- `PUT /promotion-years/{id}` - Update promotion year
- `DELETE /promotion-years/{id}` - Delete promotion year

#### Services

- `GET /services` - List all services
- `POST /services` - Create new service
- `GET /services/{id}` - Get specific service
- `PUT /services/{id}` - Update service
- `DELETE /services/{id}` - Delete service

#### Plannings

- `POST /plannings/generer/{promo_id}` - Generate basic planning
- `POST /plannings/generer-avance/{promo_id}` - Generate advanced planning
- `GET /plannings/{promo_id}` - Get promotion planning
- `GET /plannings/etudiant/{promo_id}/{etudiant_id}` - Get student schedule

#### Student Schedules

- `GET /student-schedules` - List all student schedules
- `GET /student-schedules/{id}` - Get specific student schedule
- `PUT /student-schedules/{id}` - Update student schedule
- `DELETE /student-schedules/{id}` - Delete student schedule
- `POST /student-schedules/export-excel/{schedule_id}` - Export to Excel

#### Planning Settings

- `GET /planning-settings` - Get current planning settings
- `PUT /planning-settings` - Update planning settings

### Request/Response Examples

#### Create Promotion

```bash
POST /api/promotions
Content-Type: application/json

{
  "nom": "Promotion 2024",
  "annee": 2024,
  "speciality_id": "uuid-here",
  "etudiants": [
    {"nom": "Doe", "prenom": "John"},
    {"nom": "Smith", "prenom": "Jane"}
  ]
}
```

#### Generate Planning

```bash
POST /api/plannings/generer-avance/promotion-uuid
Content-Type: application/json

{
  "date_debut": "2024-09-01",
  "date_fin": "2025-06-30",
  "services_ids": ["service-uuid-1", "service-uuid-2"]
}
```

## 🎨 Frontend Features

### Main Pages

#### 1. Dashboard (`/`)

- System overview and statistics
- Recent activities
- Quick access to main functions
- Health status monitoring

#### 2. Students (`/students`)

- Manage student cohorts and promotions
- Create and edit promotions
- Add/remove students
- View student lists and details
- Multi-year promotion management

#### 3. Planning (`/planning`)

- Generate internship schedules
- View and edit plannings
- Advanced planning algorithms
- Schedule optimization
- Conflict detection and resolution

#### 4. Settings (`/settings`)

- Manage hospital services
- Configure specialities
- Planning settings and parameters
- System configuration

### Advanced Features

#### Advanced Planning Page

- Sophisticated scheduling algorithms
- Optimization parameters
- Performance metrics
- Schedule validation

#### Student Schedules Page

- Individual student schedule management
- Progress tracking
- Schedule versioning
- Excel export functionality

#### Services Management

- Hospital department configuration
- Capacity management
- Duration settings
- Speciality associations

### UI Components

#### Reusable Components

- **Table**: Sortable, filterable data tables
- **Modal**: Confirmation and form dialogs
- **FormInput**: Validated form inputs
- **Button**: Consistent button styling
- **Badge**: Status and category indicators

#### Radix UI Integration

- **Dialog**: Accessible modal dialogs
- **Select**: Dropdown selections
- **Navigation Menu**: Main navigation
- **Avatar**: User profile components
- **Label**: Form labels

## 🚀 Installation & Setup

### Prerequisites

1. **Node.js** (v16 or higher)
2. **Python** (3.8 or higher)
3. **PostgreSQL** (12 or higher)
4. **Git**

### Backend Setup

#### 1. Install PostgreSQL

**Windows:**

```bash
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql
```

**macOS:**

```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 2. Configure PostgreSQL

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Set password for postgres user
ALTER USER postgres PASSWORD '123456789';

# Create database
CREATE DATABASE stages_paramedicaux;

# Exit PostgreSQL
\q
```

#### 3. Install Python Dependencies

```bash
cd paramedical/backend
pip install -r requirements.txt
```

#### 4. Setup Database

```bash
# Run the database setup script
python setup_db.py
```

#### 5. Run Migrations (Optional)

```bash
# Apply existing migrations
alembic upgrade head
```

#### 6. Start Backend Server

```bash
python server.py
```

The API will be available at `http://localhost:8001`

### Frontend Setup

#### 1. Install Dependencies

```bash
cd paramedical/frontend
npm install
# or
yarn install
```

#### 2. Start Development Server

```bash
npm start
# or
yarn start
```

The frontend will be available at `http://localhost:3000`

### Environment Configuration

#### Backend Environment Variables

```bash
# Database configuration
DATABASE_URL=postgresql://postgres:123456789@localhost:5432/stages_paramedicaux

# Server configuration
PORT=8001
HOST=0.0.0.0
```

#### Frontend Environment Variables

```bash
# API base URL
REACT_APP_API_URL=http://localhost:8001/api
```

## 📖 Usage Guide

### Getting Started

1. **Start the Backend**

   ```bash
   cd paramedical/backend
   python server.py
   ```

2. **Start the Frontend**

   ```bash
   cd paramedical/frontend
   npm start
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8001/docs

### Basic Workflow

#### 1. Configure Specialities

1. Go to Settings page
2. Click "Specialities" tab
3. Add medical specialities (e.g., "Infirmier", "Kinésithérapeute")

#### 2. Create Services

1. Go to Settings page
2. Click "Services" tab
3. Add hospital departments with capacities and durations

#### 3. Create Promotion

1. Go to Students page
2. Click "Create Promotion"
3. Enter promotion details and add students

#### 4. Generate Planning

1. Go to Planning page
2. Select promotion and services
3. Click "Generate Planning"
4. Review and adjust schedule

#### 5. Monitor Progress

1. Use Dashboard for overview
2. Check individual student schedules
3. Export data as needed

### Advanced Features

#### Advanced Planning

- Use advanced algorithms for optimal scheduling
- Configure planning parameters
- Analyze schedule efficiency

#### Student Schedule Management

- Track individual student progress
- Manage schedule versions
- Export schedules to Excel

#### Multi-year Support

- Manage different academic years
- Configure year-specific services
- Track student progression

## 🛠️ Development

### Backend Development

#### Code Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── crud/          # Database operations
│   ├── models.py      # Database models
│   ├── schemas.py     # Pydantic schemas
│   └── main.py        # FastAPI app
├── alembic/           # Database migrations
└── tests/             # Test files
```

#### Adding New Endpoints

1. Create endpoint in `app/api/endpoints/`
2. Add CRUD operations in `app/crud/`
3. Update schemas in `app/schemas.py`
4. Register route in `app/api/__init__.py`

#### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend Development

#### Code Structure

```
frontend/src/
├── components/        # Reusable components
├── pages/            # Main application pages
├── services/         # API communication
├── contexts/         # React contexts
└── App.js           # Main component
```

#### Adding New Pages

1. Create page component in `src/pages/`
2. Add route in `src/App.js`
3. Update navigation if needed

#### Styling

- Use Tailwind CSS classes
- Follow component library patterns
- Maintain consistent design system

### Code Quality

#### Backend

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Run tests
pytest
```

#### Frontend

```bash
# Lint code
npm run lint

# Format code
npm run format
```

## 🧪 Testing

### Backend Testing

#### Run Tests

```bash
cd paramedical/backend
python -m pytest
```

#### Test Structure

```
tests/
├── test_api/         # API endpoint tests
├── test_crud/        # Database operation tests
└── test_integration/ # Integration tests
```

### Frontend Testing

#### Run Tests

```bash
cd paramedical/frontend
npm test
```

#### Test Structure

```
src/
├── __tests__/        # Test files
└── components/       # Component tests
```

### Manual Testing

#### API Testing

1. Use Swagger UI: http://localhost:8001/docs
2. Test all endpoints with sample data
3. Verify error handling

#### Frontend Testing

1. Test all user flows
2. Verify responsive design
3. Check accessibility
4. Test error scenarios

## 🚀 Deployment

### Backend Deployment

#### Production Requirements

- PostgreSQL database
- Python 3.8+
- Gunicorn or uvicorn
- Environment variables

#### Deployment Steps

1. **Setup Database**

   ```bash
   # Create production database
   createdb stages_paramedicaux_prod
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations**

   ```bash
   alembic upgrade head
   ```

4. **Start Server**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend Deployment

#### Build for Production

```bash
npm run build
```

#### Deploy to Static Host

- Upload `build/` folder to web server
- Configure reverse proxy for API calls
- Set environment variables

### Docker Deployment

#### Backend Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Frontend Dockerfile

```dockerfile
FROM node:16-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
```

## 🔧 Troubleshooting

### Common Issues

#### Backend Issues

**Database Connection**

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d stages_paramedicaux
```

**Port Already in Use**

```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>
```

**Migration Issues**

```bash
# Reset migrations
alembic downgrade base
alembic upgrade head
```

#### Frontend Issues

**Build Failures**

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
```

**API Connection**

- Check backend server is running
- Verify API URL in environment
- Check CORS configuration

### Debug Mode

#### Backend Debug

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python server.py
```

#### Frontend Debug

```bash
# Enable React DevTools
npm start
# Open browser DevTools
```

### Logs

#### Backend Logs

- Check console output for errors
- Database connection logs
- API request/response logs

#### Frontend Logs

- Browser console for JavaScript errors
- Network tab for API calls
- React DevTools for component state

## 📚 Additional Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### API Documentation

- Interactive API docs: http://localhost:8001/docs
- ReDoc documentation: http://localhost:8001/redoc

### Development Tools

- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - Database management
- [React DevTools](https://chrome.google.com/webstore/detail/react-developer-tools) - React debugging

## 📄 License

This project is part of the Stages Paramédicaux management system.

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainer**: Development Team
