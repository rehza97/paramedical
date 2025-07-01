# API Documentation - Stages Paramédicaux

## Base URL

```
http://localhost:8001/api
```

## Authentication

Currently no authentication required. All endpoints are public.

---

## Health Check

### GET /health

Check service health status.

**Response:**

```json
{
  "status": "healthy",
  "service": "stages-paramedicaux-api"
}
```

---

## Promotions

### POST /promotions

Create a new promotion with students.

**Request Body:**

```json
{
  "nom": "Promotion 2025",
  "annee": 2025,
  "etudiants": [
    {
      "nom": "Dupont",
      "prenom": "Jean"
    },
    {
      "nom": "Martin",
      "prenom": "Marie"
    }
  ]
}
```

**Response:**

```json
{
  "id": "uuid-string",
  "message": "Promotion créée avec succès"
}
```

### GET /promotions

Get all promotions.

**Query Parameters:**

- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records (default: 100)

**Response:**

```json
[
  {
    "id": "uuid-string",
    "nom": "Promotion 2025",
    "annee": 2025,
    "date_creation": "2024-01-01T00:00:00",
    "etudiants": [
      {
        "id": "uuid-string",
        "nom": "Dupont",
        "prenom": "Jean",
        "promotion_id": "uuid-string"
      }
    ]
  }
]
```

### GET /promotions/{promotion_id}

Get a specific promotion by ID.

**Response:**

```json
{
  "id": "uuid-string",
  "nom": "Promotion 2025",
  "annee": 2025,
  "date_creation": "2024-01-01T00:00:00",
  "etudiants": [...]
}
```

### DELETE /promotions/{promotion_id}

Delete a promotion and all associated data.

**Response:**

```json
{
  "message": "Promotion supprimée avec succès"
}
```

---

## Services

### POST /services

Create a new service.

**Request Body:**

```json
{
  "nom": "Cardiologie",
  "places_disponibles": 5,
  "duree_stage_jours": 30
}
```

**Response:**

```json
{
  "id": "uuid-string",
  "message": "Service créé avec succès"
}
```

### GET /services

Get all services.

**Query Parameters:**

- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records (default: 100)

**Response:**

```json
[
  {
    "id": "uuid-string",
    "nom": "Cardiologie",
    "places_disponibles": 5,
    "duree_stage_jours": 30,
    "date_creation": "2024-01-01T00:00:00"
  }
]
```

### GET /services/{service_id}

Get a specific service by ID.

### PUT /services/{service_id}

Update a service.

**Request Body:**

```json
{
  "nom": "Cardiologie Interventionnelle",
  "places_disponibles": 3,
  "duree_stage_jours": 45
}
```

### DELETE /services/{service_id}

Delete a service.

---

## Plannings

### POST /plannings/generer/{promo_id}

Generate basic planning for a promotion.

**Query Parameters:**

- `date_debut` (optional): Start date in YYYY-MM-DD format (default: "2025-01-01")

**Response:**

```json
{
  "message": "Planning généré avec succès",
  "planning": {
    "id": "uuid-string",
    "promo_id": "uuid-string",
    "date_creation": "2024-01-01T00:00:00",
    "promo_nom": "Promotion 2025",
    "rotations": [
      {
        "id": "uuid-string",
        "etudiant_id": "uuid-string",
        "service_id": "uuid-string",
        "date_debut": "2025-01-01",
        "date_fin": "2025-01-30",
        "ordre": 1,
        "planning_id": "uuid-string",
        "etudiant_nom": "Jean Dupont",
        "service_nom": "Cardiologie"
      }
    ]
  }
}
```

### 🆕 POST /plannings/generer-avance/{promo_id}

Generate advanced planning with intelligent load balancing.

**Query Parameters:**

- `date_debut` (optional): Start date in YYYY-MM-DD format (default: "2025-01-01")

**Response:**

```json
{
  "message": "Planning avancé généré avec succès",
  "planning": {
    "id": "uuid-string",
    "promo_id": "uuid-string",
    "date_creation": "2024-01-01T00:00:00",
    "promo_nom": "Promotion 2025",
    "rotations": [...]
  },
  "efficiency_analysis": {
    "duree_totale_jours": 365,
    "date_debut": "2025-01-01",
    "date_fin": "2025-12-31",
    "nb_rotations": 120,
    "occupation_services": {
      "Cardiologie": {
        "taux_occupation": 85.5,
        "jours_actifs": 300,
        "occupation_moyenne": 4.3
      },
      "Pneumologie": {
        "taux_occupation": 92.1,
        "jours_actifs": 280,
        "occupation_moyenne": 2.8
      }
    }
  },
  "validation_result": {
    "is_valid": true,
    "erreurs": []
  }
}
```

### 🆕 POST /plannings/analyser-efficacite/{promo_id}

Analyze the efficiency of an existing planning.

**Response:**

```json
{
  "duree_totale_jours": 365,
  "date_debut": "2025-01-01",
  "date_fin": "2025-12-31",
  "nb_rotations": 120,
  "occupation_services": {
    "Cardiologie": {
      "taux_occupation": 85.5,
      "jours_actifs": 300,
      "occupation_moyenne": 4.3
    }
  }
}
```

### 🆕 POST /plannings/valider/{promo_id}

Validate an existing planning and return any errors.

**Response:**

```json
{
  "is_valid": false,
  "erreurs": [
    "Dépassement de capacité dans 'Cardiologie' le 2025-03-15: 6 étudiants pour 5 places disponibles",
    "Étudiant Marie Martin n'a pas été assigné aux services: Pneumologie, Neurologie"
  ]
}
```

### GET /plannings/{promo_id}

Get planning for a promotion.

**Response:**

```json
{
  "id": "uuid-string",
  "promo_id": "uuid-string",
  "date_creation": "2024-01-01T00:00:00",
  "promo_nom": "Promotion 2025",
  "rotations": [...]
}
```

### GET /plannings/etudiant/{promo_id}/{etudiant_id}

Get planning for a specific student.

**Response:**

```json
{
  "etudiant_id": "uuid-string",
  "rotations": [
    {
      "id": "uuid-string",
      "etudiant_id": "uuid-string",
      "service_id": "uuid-string",
      "date_debut": "2025-01-01",
      "date_fin": "2025-01-30",
      "ordre": 1,
      "planning_id": "uuid-string",
      "etudiant_nom": "Jean Dupont",
      "service_nom": "Cardiologie"
    }
  ]
}
```

---

## Advanced Planning Algorithm

### 🧠 Algorithm Features

The advanced planning algorithm (`/plannings/generer-avance/{promo_id}`) uses sophisticated scoring to optimize internship assignments:

#### Scoring System

- **Availability Score (40%)**: Prioritizes immediately available services
- **Capacity Score (25%)**: Favors services with higher capacity
- **Urgency Score (25%)**: Prioritizes bottleneck services
- **Duration Score (10%)**: Slightly favors longer internships

#### Key Benefits

1. **Optimal Resource Utilization**: Maximizes service capacity usage
2. **Flexible Scheduling**: Adapts to varying service constraints
3. **Conflict Resolution**: Automatically handles scheduling conflicts
4. **Load Balancing**: Distributes students evenly across time periods

### 📊 Efficiency Metrics

The efficiency analysis provides:

- **Total Duration**: Overall planning timespan
- **Occupation Rates**: Percentage utilization per service
- **Active Days**: Number of days each service is used
- **Average Occupation**: Average number of students per service

### ✅ Validation Checks

The validation system checks for:

- **Capacity Overruns**: More students than available places
- **Missing Assignments**: Students not assigned to all required services
- **Scheduling Conflicts**: Overlapping assignments
- **Resource Constraints**: Invalid service configurations

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Error message describing the issue"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity

```json
{
  "detail": "Validation error message"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error message"
}
```

---

## Example Usage

### Complete Workflow

1. **Create Services:**

```bash
curl -X POST "http://localhost:8001/api/services" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Cardiologie",
    "places_disponibles": 5,
    "duree_stage_jours": 30
  }'
```

2. **Create Promotion:**

```bash
curl -X POST "http://localhost:8001/api/promotions" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Promotion 2025",
    "annee": 2025,
    "etudiants": [
      {"nom": "Dupont", "prenom": "Jean"},
      {"nom": "Martin", "prenom": "Marie"}
    ]
  }'
```

3. **Generate Advanced Planning:**

```bash
curl -X POST "http://localhost:8001/api/plannings/generer-avance/PROMO_ID?date_debut=2025-01-01"
```

4. **Validate Planning:**

```bash
curl -X POST "http://localhost:8001/api/plannings/valider/PROMO_ID"
```

5. **Analyze Efficiency:**

```bash
curl -X POST "http://localhost:8001/api/plannings/analyser-efficacite/PROMO_ID"
```

---

## Notes

- All dates are in ISO 8601 format (YYYY-MM-DD)
- UUIDs are used for all entity identifiers
- The advanced algorithm can handle complex scheduling scenarios
- Validation provides detailed error messages for troubleshooting
- Efficiency analysis helps optimize resource allocation
