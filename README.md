# AI Support Platform

AI Support Platform is an AI-powered support platform for monitoring, investigating, and resolving recurring customer issues. It combines support ticket analytics, semantic search, anomaly detection, clustering, and LLM-assisted insights in a single workflow.

## Architecture

```text
┌───────────────────────┐
│ React + TypeScript     │
│ Dashboard + UI         │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ Spring Boot API        │
│ JWT auth + tickets +  │
│ analytics + simulator  │
└───────┬───────────────┘
        │
   ┌────┼────┐
   │    │
   ▼    ▼
┌────────────┐  ┌────────────────────┐
│ PostgreSQL │  │ Python ML Service  │
│ + pgvector │  │ FastAPI + HDBSCAN  │
└────────────┘  │ embeddings + stats │
                └─────────┬──────────┘
                          ▼
                   LLM API (OpenAI)
```

## Features

- JWT authentication and role-based access
- Ticket management and issue lifecycle tracking
- Semantic search with pgvector embeddings
- HDBSCAN-based clustering of related tickets
- Z-score anomaly detection for spikes in support volume
- Emerging issue detection and root-cause hints
- RAG-style ask-the-data experience over support records
- Dashboard analytics and simulation scenarios

## Tech Stack

### Backend
- Java 21
- Spring Boot 3
- Spring Security
- Spring Data JPA / Hibernate
- PostgreSQL 16 + pgvector
- Flyway

### ML / AI
- Python 3.11
- FastAPI
- scikit-learn / HDBSCAN
- NumPy / SciPy
- OpenAI integration

### Frontend
- React 18
- TypeScript
- Vite

### Infrastructure
- Docker / Docker Compose
- GitHub Actions
- Testcontainers

## Prerequisites

- Docker and Docker Compose
- Or: Java 21, Python 3.11, Node.js 18+, PostgreSQL 16

## Quick Start

### Option 1: Docker Compose

```bash
git clone <your-repo-url>
cd "AI Support Platform"
cp server-java/.env.example server-java/.env
docker compose up --build
```

Available services:
- Backend: http://localhost:8080
- Swagger UI: http://localhost:8080/swagger-ui.html
- ML service: http://localhost:8000
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432

### Option 2: Local development

Backend:
```bash
cd server-java
mvn clean install
mvn spring-boot:run
```

ML service:
```bash
cd ml-service
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd client
npm install
npm run dev
```

## Main API Endpoints

### Authentication
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

### Tickets
- `GET /api/v1/tickets`
- `POST /api/v1/tickets`
- `GET /api/v1/tickets/{id}`
- `PUT /api/v1/tickets/{id}`
- `DELETE /api/v1/tickets/{id}`

### Search and analytics
- `POST /api/v1/search/semantic`
- `GET /api/v1/analytics/summary`
- `GET /api/v1/analytics/clustering`
- `GET /api/v1/analytics/anomalies`

### RAG and simulator
- `POST /api/v1/rag/query`
- `POST /api/v1/simulator/scenarios/visa-outage`
- `POST /api/v1/simulator/scenarios/login-bug`
- `POST /api/v1/simulator/scenarios/mobile-crash`

## Configuration

Set the required environment variables in `server-java/.env` or via your shell.

Key variables:
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `JWT_SECRET`
- `ML_SERVICE_URL`
- `CORS_ALLOWED_ORIGINS`
- `LLM_API_KEY`

## Testing

```bash
cd server-java
mvn test
```

```bash
cd ml-service
pytest tests/ -v
```

## Roadmap

- [x] Foundation and API layer
- [x] JWT auth and security
- [x] ML service and embeddings
- [x] Clustering pipeline
- [x] Anomaly detection
- [x] Emerging issue detection
- [x] LLM-assisted support insights
- [ ] Real-time dashboard refinements
- [ ] CI/CD and production polish

## License

MIT

## 🤝 Contributing

Contributions welcome! Please open issues and PRs.

## 📞 Contact

For questions or feedback, reach out via GitHub Issues.

---

**Status:** In active development (Milestones 1-8 complete, 9-10 pending)
