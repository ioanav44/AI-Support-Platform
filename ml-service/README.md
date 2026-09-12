# ML Service README

Python FastAPI service pentru embeddings, clustering și anomaly detection.

## Features

- **Embeddings**: Sentence Transformers (384-dim) cu model `all-MiniLM-L6-v2`
- **Clustering**: HDBSCAN pentru detecție incremental de cluster-uri
- **Anomaly Detection**: Z-score bazat pe metrici
- **REST API**: Endpoints pentru embeding, clustering, anomaly detection

## Setup

```bash
pip install -r requirements.txt
```

## Run Local

```bash
uvicorn app.main:app --reload --port 8000
```

API disponibil la `http://localhost:8000`

Docs la `http://localhost:8000/docs`

## Endpoints

### Embeddings
- `POST /api/v1/embeddings/generate` - Generate embedding pentru text
- `POST /api/v1/embeddings/generate-batch` - Generate embeddings pentru lista de texte

### Clustering
- `POST /api/v1/clustering/cluster` - Cluster embeddings cu HDBSCAN

### Anomalies
- `POST /api/v1/anomalies/detect` - Detect anomalies cu Z-score
- `POST /api/v1/anomalies/baseline` - Update baseline pentru metric

## Architecture

```
app/
├── config.py                 (Settings cu env vars)
├── models/
│   ├── embedding.py         (SentenceTransformer singleton)
│   └── anomaly.py           (Z-score detector)
├── services/
│   └── clustering.py        (HDBSCAN service)
├── api/
│   ├── schemas.py           (Request/Response models)
│   ├── embeddings.py        (Embedding endpoints)
│   └── ml_routes.py         (Clustering + Anomaly endpoints)
└── main.py                  (FastAPI app)
```

## Docker

```bash
docker build -t pulseai-ml:latest .
docker run -p 8000:8000 \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  pulseai-ml:latest
```

## Integration cu Spring Boot

Spring Boot chiama ML service:
- `MLServiceClient.generateEmbedding(text)` → embedding
- `MLServiceClient.clusterEmbeddings(embeddings)` → cluster labels + outlier scores

Configurație în `application.yaml`:
```yaml
ml:
  service:
    url: http://localhost:8000
```
