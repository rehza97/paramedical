# Stages Paramédicaux Backend

This is the backend API for the Stages Paramédicaux (Paramedical Internships) management system, built with FastAPI and PostgreSQL.

## 🏗️ Architecture

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Port**: 8001

## 📋 Prerequisites

1. **Python 3.8+**
2. **PostgreSQL** installed and running
3. **pip** for package management

## 🚀 Setup Instructions

### 1. Install PostgreSQL

#### On Windows:

```bash
# Download and install from https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql
```

#### On macOS:

```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

#### On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Configure PostgreSQL

```bash
# Connect to PostgreSQL as postgres user
sudo -u postgres psql

# Set password for postgres user
ALTER USER postgres PASSWORD '123456789';

# Create database (optional - setup script will do this)
CREATE DATABASE stages_paramedicaux;

# Exit PostgreSQL
\q
```

### 3. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Setup Database

```bash
# Run the database setup script
python setup_db.py
```

This will:

- Create the database if it doesn't exist
- Create all necessary tables
- Set up the schema

### 5. Run Migrations (Optional)

If you need to make database schema changes:

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

### 6. Start the Server

```bash
python server.py
```

The API will be available at `http://localhost:8001`

## 🧪 Testing

Run the test suite:

```bash
python backend_test.py
```

## 📊 Database Schema

### Tables

1. **promotions** - Student cohorts

   - id (UUID, Primary Key)
   - nom (String)
   - annee (Integer)
   - date_creation (DateTime)

2. **etudiants** - Students

   - id (UUID, Primary Key)
   - nom (String)
   - prenom (String)
   - promotion_id (UUID, Foreign Key)

3. **services** - Hospital departments

   - id (UUID, Primary Key)
   - nom (String, Unique)
   - places_disponibles (Integer)
   - duree_stage_jours (Integer)
   - date_creation (DateTime)

4. **plannings** - Internship schedules

   - id (UUID, Primary Key)
   - promo_id (UUID, Foreign Key)
   - date_creation (DateTime)

5. **rotations** - Individual student rotations
   - id (UUID, Primary Key)
   - etudiant_id (UUID, Foreign Key)
   - service_id (UUID, Foreign Key)
   - planning_id (UUID, Foreign Key)
   - date_debut (String, YYYY-MM-DD)
   - date_fin (String, YYYY-MM-DD)
   - ordre (Integer)

## 🔧 Environment Variables

You can customize the database connection by setting the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://username:password@host:port/database"
```

Default configuration:

- Host: localhost
- Port: 5432
- Database: stages_paramedicaux
- Username: postgres
- Password: 123456789

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8001/docs
- **ReDoc documentation**: http://localhost:8001/redoc

## 🔍 API Endpoints

### Health Check

- `GET /api/health` - Service status

### Promotions

- `POST /api/promotions` - Create promotion
- `GET /api/promotions` - List all promotions
- `GET /api/promotions/{id}` - Get specific promotion
- `DELETE /api/promotions/{id}` - Delete promotion

### Services

- `POST /api/services` - Create service
- `GET /api/services` - List all services
- `PUT /api/services/{id}` - Update service
- `DELETE /api/services/{id}` - Delete service

### Plannings

- `POST /api/plannings/generer/{promo_id}` - Generate planning
- `GET /api/plannings/{promo_id}` - Get promotion planning
- `GET /api/plannings/etudiant/{promo_id}/{etudiant_id}` - Get student schedule

## 🐛 Troubleshooting

### Common Issues

1. **Connection refused to PostgreSQL**

   - Ensure PostgreSQL is running
   - Check if the service is started: `sudo systemctl status postgresql`

2. **Authentication failed**

   - Verify the password is correct
   - Check pg_hba.conf configuration

3. **Database doesn't exist**

   - Run the setup script: `python setup_db.py`

4. **Port already in use**
   - Change the port in `server.py` or kill the process using port 8001

### Logs

Check the console output for detailed error messages and debugging information.

## 🔄 Migration from MongoDB

This version has been migrated from MongoDB to PostgreSQL. The main changes include:

- Replaced PyMongo with SQLAlchemy
- Added proper database relationships
- Implemented database migrations with Alembic
- Enhanced data validation with Pydantic schemas
- Improved transaction handling

## 📝 License

This project is part of the Stages Paramédicaux management system.

This is the backend API for the Stages Paramédicaux (Paramedical Internships) management system, built with FastAPI and PostgreSQL.

## 🏗️ Architecture

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Port**: 8001

## 📋 Prerequisites

1. **Python 3.8+**
2. **PostgreSQL** installed and running
3. **pip** for package management

## 🚀 Setup Instructions

### 1. Install PostgreSQL

#### On Windows:

```bash
# Download and install from https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql
```

#### On macOS:

```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

#### On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Configure PostgreSQL

```bash
# Connect to PostgreSQL as postgres user
sudo -u postgres psql

# Set password for postgres user
ALTER USER postgres PASSWORD '123456789';

# Create database (optional - setup script will do this)
CREATE DATABASE stages_paramedicaux;

# Exit PostgreSQL
\q
```

### 3. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Setup Database

```bash
# Run the database setup script
python setup_db.py
```

This will:

- Create the database if it doesn't exist
- Create all necessary tables
- Set up the schema

### 5. Run Migrations (Optional)

If you need to make database schema changes:

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

### 6. Start the Server

```bash
python server.py
```

The API will be available at `http://localhost:8001`

## 🧪 Testing

Run the test suite:

```bash
python backend_test.py
```

## 📊 Database Schema

### Tables

1. **promotions** - Student cohorts

   - id (UUID, Primary Key)
   - nom (String)
   - annee (Integer)
   - date_creation (DateTime)

2. **etudiants** - Students

   - id (UUID, Primary Key)
   - nom (String)
   - prenom (String)
   - promotion_id (UUID, Foreign Key)

3. **services** - Hospital departments

   - id (UUID, Primary Key)
   - nom (String, Unique)
   - places_disponibles (Integer)
   - duree_stage_jours (Integer)
   - date_creation (DateTime)

4. **plannings** - Internship schedules

   - id (UUID, Primary Key)
   - promo_id (UUID, Foreign Key)
   - date_creation (DateTime)

5. **rotations** - Individual student rotations
   - id (UUID, Primary Key)
   - etudiant_id (UUID, Foreign Key)
   - service_id (UUID, Foreign Key)
   - planning_id (UUID, Foreign Key)
   - date_debut (String, YYYY-MM-DD)
   - date_fin (String, YYYY-MM-DD)
   - ordre (Integer)

## 🔧 Environment Variables

You can customize the database connection by setting the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://username:password@host:port/database"
```

Default configuration:

- Host: localhost
- Port: 5432
- Database: stages_paramedicaux
- Username: postgres
- Password: 123456789

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8001/docs
- **ReDoc documentation**: http://localhost:8001/redoc

## 🔍 API Endpoints

### Health Check

- `GET /api/health` - Service status

### Promotions

- `POST /api/promotions` - Create promotion
- `GET /api/promotions` - List all promotions
- `GET /api/promotions/{id}` - Get specific promotion
- `DELETE /api/promotions/{id}` - Delete promotion

### Services

- `POST /api/services` - Create service
- `GET /api/services` - List all services
- `PUT /api/services/{id}` - Update service
- `DELETE /api/services/{id}` - Delete service

### Plannings

- `POST /api/plannings/generer/{promo_id}` - Generate planning
- `GET /api/plannings/{promo_id}` - Get promotion planning
- `GET /api/plannings/etudiant/{promo_id}/{etudiant_id}` - Get student schedule

## 🐛 Troubleshooting

### Common Issues

1. **Connection refused to PostgreSQL**

   - Ensure PostgreSQL is running
   - Check if the service is started: `sudo systemctl status postgresql`

2. **Authentication failed**

   - Verify the password is correct
   - Check pg_hba.conf configuration

3. **Database doesn't exist**

   - Run the setup script: `python setup_db.py`

4. **Port already in use**
   - Change the port in `server.py` or kill the process using port 8001

### Logs

Check the console output for detailed error messages and debugging information.

## 🔄 Migration from MongoDB

This version has been migrated from MongoDB to PostgreSQL. The main changes include:

- Replaced PyMongo with SQLAlchemy
- Added proper database relationships
- Implemented database migrations with Alembic
- Enhanced data validation with Pydantic schemas
- Improved transaction handling

## 📝 License

This project is part of the Stages Paramédicaux management system.
