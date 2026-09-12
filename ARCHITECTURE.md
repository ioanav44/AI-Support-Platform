# AI Support Platform - Technical Architecture

## System Design

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│              (React + TypeScript Dashboard)                 │
└────────────────────┬────────────────────────────────────────┘
                     │ REST + SSE
┌────────────────────▼────────────────────────────────────────┐
│                  API Gateway Layer                          │
│         (Spring Boot + Spring Security + JWT)               │
└────┬──────────────────────────┬──────────────────────┬──────┘
     │                          │                      │
     ▼                          ▼                      ▼
┌─────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│  Business   │  │   ML Services    │  │  External Services   │
│  Logic      │  │   Integration    │  │  (LLM, Analytics)    │
│  Layer      │  │   Layer          │  │                      │
└──────┬──────┘  └────────┬─────────┘  └──────────┬───────────┘
       │                  │                       │
       └──────────────────┼───────────────────────┘
                          │ JDBC + REST
┌─────────────────────────▼────────────────────────────────────┐
│                   Data Layer                                 │
│       (PostgreSQL 16 + pgvector + Python ML Service)         │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Spring Boot Backend

#### Controllers
```
├── AuthController          # Login, register, refresh token
├── TicketController        # Ticket CRUD operations
├── SearchController        # Semantic search
├── EmergingIssueController # Issue tracking & updates
├── AnalyticsController     # Metrics & clustering results
├── RAGController           # "Ask Support Data"
└── SimulatorController     # Test scenarios (ADMIN only)
```

#### Services
```
├── AuthService             # User authentication & JWT management
├── TicketService           # Ticket operations + embedding generation
├── ClusteringService       # Scheduled clustering pipeline
├── EmergingIssueService    # Issue detection & lifecycle
├── AnalyticsService        # Dashboard metrics aggregation
├── RAGService              # Question answering with LLM
└── SimulatorService        # Scenario data generation
```

#### Repositories
```
├── UserRepository          # User queries + custom methods
├── RoleRepository          # Role management
├── TicketRepository        # Ticket queries + pgvector similarity search
└── EmergingIssueRepository # Issue tracking
```

#### Security
```
├── JwtTokenProvider        # Token generation & validation
├── JwtAuthenticationFilter # Request-level JWT verification
├── SecurityConfig          # Spring Security configuration
└── Role-based @PreAuthorize annotations
```

#### Data Access
```
├── JPA/Hibernate ORM       # Object-relational mapping
├── Flyway Migrations       # Version-controlled schema
├── pgvector Integration    # Vector similarity queries
└── Connection Pooling      # HikariCP (10 max, 2 min)
```

### 2. Python ML Service (FastAPI)

```
├── app/
│   ├── main.py             # FastAPI entry point, routes
│   ├── config.py           # Settings & environment vars
│   ├── models/
│   │   ├── embedding.py    # SentenceTransformer singleton
│   │   └── anomaly.py      # Z-score detector
│   ├── services/
│   │   ├── clustering.py   # HDBSCAN implementation
│   │   └── storage.py      # PostgreSQL connection (optional)
│   └── api/
│       ├── schemas.py      # Pydantic request/response models
│       ├── embeddings.py   # /api/v1/embeddings endpoints
│       └── ml_routes.py    # /api/v1/clustering, /api/v1/anomalies
├── requirements.txt        # Dependencies
├── Dockerfile              # Python 3.11 slim + uvicorn
└── README.md               # Service documentation
```

#### Key Endpoints
```
POST   /api/v1/embeddings/generate        # Single text embedding
POST   /api/v1/embeddings/generate-batch  # Batch embeddings
POST   /api/v1/clustering/cluster         # HDBSCAN clustering
POST   /api/v1/anomalies/detect           # Z-score anomaly detection
POST   /api/v1/anomalies/baseline         # Compute baseline stats
GET    /health                            # Health check
```

### 3. Database Schema

#### Core Tables
```sql
users
  ├── id (PK)
  ├── username (UNIQUE)
  ├── email (UNIQUE)
  ├── password_hash
  ├── enabled
  └── timestamps

roles
  ├── id (PK)
  ├── name (ADMIN, ANALYST)
  └── description

user_roles
  ├── user_id (FK)
  ├── role_id (FK)
  └── (composite PK)

tickets
  ├── id (PK)
  ├── title
  ├── description (TEXT)
  ├── status (OPEN|IN_PROGRESS|RESOLVED|CLOSED)
  ├── priority (LOW|MEDIUM|HIGH|CRITICAL)
  ├── sentiment_score (DOUBLE)
  ├── embedding (vector[384])      ← pgvector column
  ├── cluster_id (INTEGER)
  ├── outlier_score (DOUBLE)
  ├── is_anomaly (BOOLEAN)
  ├── assigned_to_id (FK)
  ├── created_by_id (FK)
  ├── created_at, updated_at, resolved_at
  └── (indexes on status, cluster_id, embedding)

emerging_issues
  ├── id (PK)
  ├── title
  ├── description (TEXT)
  ├── severity (LOW|MEDIUM|HIGH|CRITICAL)
  ├── status (DETECTED|INVESTIGATING|RESOLVED|CLOSED)
  ├── detected_at, resolved_at
  ├── created_by_id (FK)
  └── timestamps

emerging_issue_tickets
  ├── issue_id (FK)
  ├── ticket_id (FK)
  └── (composite PK)
```

#### Indexes
```sql
-- Performance optimization
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_cluster_id ON tickets(cluster_id);
CREATE INDEX idx_tickets_is_anomaly ON tickets(is_anomaly);
CREATE INDEX idx_tickets_embedding ON tickets USING ivfflat (
  embedding vector_cosine_ops
);
CREATE INDEX idx_emerging_issues_status ON emerging_issues(status);
CREATE INDEX idx_emerging_issues_severity ON emerging_issues(severity);
```

### 4. Data Flow

#### Ticket Creation Flow
```
1. POST /api/v1/tickets
   ├─> AuthController validates JWT
   ├─> TicketService.createTicket()
   │   ├─> Save to PostgreSQL
   │   ├─> Call MLServiceClient.generateEmbedding()
   │   │   └─> POST to Python service
   │   └─> Store embedding in tickets.embedding (pgvector)
   └─> Return TicketDTO
```

#### Semantic Search Flow
```
1. POST /api/v1/search/semantic
   ├─> SearchController.semanticSearch()
   ├─> TicketService.semanticSearch(query)
   │   ├─> Call MLServiceClient.generateEmbedding(query)
   │   ├─> Query: SELECT * FROM tickets WHERE embedding <-> query_embedding
   │   └─> Return Top-K results
   └─> Return TicketDTO[] ordered by similarity
```

#### Clustering Pipeline Flow (Every 5 minutes)
```
1. @Scheduled(fixedRate = 300000)
   ├─> ClusteringService.runClusteringPipeline()
   ├─> Fetch all tickets with embeddings
   ├─> Call MLServiceClient.clusterEmbeddings(embeddings)
   │   └─> POST to Python: HDBSCAN clustering
   ├─> Update tickets with cluster_id, outlier_score, is_anomaly
   ├─> Detect clusters with >= 3 tickets
   ├─> Create EmergingIssue if new cluster detected
   └─> Log results
```

#### RAG Query Flow
```
1. POST /api/v1/rag/query
   ├─> RAGController.querySupport()
   ├─> RAGService.queryKnowledgeBase(question)
   │   ├─> Semantic search: TicketService.semanticSearch(top 5)
   │   ├─> Extract context from results
   │   ├─> Call LLMServiceClient.generateAnswer(question, context)
   │   │   └─> POST to OpenAI with prompt
   │   └─> Return synthesized answer
   └─> Return RAGResponse with question + answer
```

## Security Model

### JWT Authentication
```
Access Token:
- Algorithm: HS512
- Expiration: 15 minutes (900,000 ms)
- Contains: username, roles, issued_at, expires_at
- Stored in: Authorization: Bearer {token} header

Refresh Token:
- Algorithm: HS512
- Expiration: 7 days (604,800,000 ms)
- Contains: username, token_type
- Purpose: Obtain new access token without re-login
```

### Authorization
```
Role-Based Access Control (RBAC):

ADMIN:
  ├─ All read operations
  ├─ All write operations
  └─ Admin-only: DELETE, simulator, role management

ANALYST:
  ├─ Read: tickets, emerging issues, analytics
  ├─ Write: create tickets, update own tickets
  ├─ Search & RAG: full access
  └─ Restricted: DELETE, simulator, user management
```

### Password Security
```
- Hashing: BCrypt (Spring Security default)
- Salt: Automatically generated per password
- Strength: 10 strength rounds
- Never logged or exposed in responses
```

## Performance Optimization

### Database
```
- Connection Pooling: HikariCP (10 max connections)
- Batch Operations: 20 inserts/updates per batch
- Lazy Loading: FetchType.LAZY on foreign keys
- Indexes: Covering indexes on frequently queried columns
- pgvector IVFFlat: ~1000x faster similarity search vs brute force
```

### Caching
```
- SentenceTransformer Model: Singleton pattern (avoid reload)
- Frequently accessed roles: Spring Security caching
- DTO conversion: Lazy on demand
- Database queries: Spring Data JPA caching (optional)
```

### Async & Scheduling
```
- Clustering: @Scheduled(fixedRate = 300000) ← Every 5 min
- No blocking I/O: RestTemplate for ML service calls
- Transaction isolation: DEFAULT (READ_COMMITTED)
```

## Deployment Considerations

### Environment-Specific Config
```
development:
  - DDL: validate (manual migrations)
  - Logging: DEBUG level
  - CORS: localhost origins
  - LLM: optional (can be disabled)

production:
  - DDL: validate only
  - Logging: INFO level
  - CORS: production domains only
  - LLM: required (OpenAI key)
  - SSL/TLS: nginx reverse proxy
  - Secrets: AWS Secrets Manager or HashiCorp Vault
```

### Scalability
```
Horizontal:
  - Stateless API design (JWT instead of sessions)
  - Spring Boot instances: Load balanced via nginx/ALB
  - Database: PostgreSQL read replicas for analytics

Vertical:
  - ML Service: GPU acceleration (CUDA for SentenceTransformers)
  - Database: Connection pool tuning, query optimization
  - Cache layer: Redis for distributed caching
```

### Monitoring & Observability
```
Logging:
  - SLF4J with Logback
  - Separate logs: application, security, database
  - Log rotation: Daily, 30-day retention

Metrics:
  - Micrometer integration (future)
  - JVM metrics: memory, GC, threads
  - Business metrics: tickets/hour, anomalies detected

Tracing:
  - Spring Cloud Sleuth (future)
  - Distributed tracing: OpenTelemetry

Health Checks:
  - Spring Boot Actuator /actuator/health
  - Database connectivity
  - ML Service availability
```

## Testing Strategy

### Unit Tests
```
- AuthService: token generation, validation, refresh
- JwtTokenProvider: encoding, decoding, expiration
- TicketService: CRUD operations (mocked dependencies)
- ClusteringService: cluster detection logic
```

### Integration Tests
```
- Testcontainers: PostgreSQL in Docker
- MockMvc: Spring MVC layer
- RestTemplate: HTTP client simulation
- Full stack: Auth → Ticket creation → Search
```

### ML Service Tests
```
- Embedding generation: verify 384-dim output
- Clustering: verify cluster labels range
- Anomaly detection: verify Z-score calculation
- API contracts: request/response schemas
```

## Scope of this version

This project intentionally focuses on the core support intelligence capabilities that are implemented and validated in this repository:

- authentication and authorization
- ticket management
- semantic search using embeddings
- ticket clustering and issue grouping
- anomaly detection based on volume and sentiment
- emerging incident detection
- dashboard analytics
- AI-assisted support query via RAG
- scenario-based simulation and validation

Additional capabilities such as real-time streaming, forecasting, multi-tenancy, compliance workflows, or mobile clients are intentionally out of scope for this version and can be considered later as separate roadmap work.

---

**Last Updated:** 2026
**Version:** 1.0.0 (implemented scope)
