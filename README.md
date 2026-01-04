# VectorShift Pipeline Builder & Analyzer

A full-stack application for visually building data pipelines and validating them as **Directed Acyclic Graphs (DAGs)**.
The system includes a **React + React Flow frontend** and a **FastAPI backend** that performs graph analysis, caching, and validation.

This project was built as part of the **VectorShift Frontend Technical Assessment**, with additional production-grade backend architecture, testing, and CI.

---

## Features

### Frontend

* Visual pipeline editor built with **React Flow**
* Schema-driven, extensible node system
* Dynamic node handles (e.g. `{{variable}}` parsing in Text nodes)
* Auto-resizing text nodes
* Category-based node toolbar
* Modern UI with TailwindCSS
* Pipeline submission with validation feedback

### Backend

* **FastAPI** service for pipeline analysis
* DAG detection using **NetworkX**
* Rate limiting with **SlowAPI**
* In-memory caching (Redis-ready abstraction)
* Request logging middleware
* Health & metrics endpoints
* Fully modular, scalable architecture
* Comprehensive **pytest** test suite
* Dockerized for production
* CI with GitHub Actions

---

## Repository Structure

```text
.
├── frontend/
│   ├── src/
│   │   ├── nodes/              # Node factory & schemas
│   │   ├── components/         # BaseNode, FieldRenderer
│   │   ├── hooks/              # Dynamic handle logic
│   │   ├── store.js            # Zustand state
│   │   └── ...
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/                # API routes
│   │   ├── core/               # Config, logging, lifespan
│   │   ├── middleware/         # Request logging
│   │   ├── models/             # Pydantic models
│   │   ├── services/           # Business logic
│   │   ├── utils/              # Helpers
│   │   └── main.py             # App bootstrap
│   ├── tests/                  # Pytest suite
│   ├── Dockerfile
│   └── requirements.txt
│
└── README.md
```

---

## Tech Stack

### Frontend

* **React**
* **React Flow**
* **Zustand**
* **Tailwind CSS**
* **NextUI**
* **React Icons**

### Backend

* **FastAPI**
* **NetworkX**
* **Pydantic**
* **SlowAPI**
* **Uvicorn**

### Tooling

* **pytest + pytest-cov**
* **Docker**
* **GitHub Actions**

---

## ▶Running Locally

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at:
`http://localhost:3000`

---

### Backend (Local)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:
`http://localhost:8000`

API Docs:
`http://localhost:8000/api/docs`

---

### Backend (Docker)

```bash
cd backend
docker build -t pipeline-api .
docker run -p 8000:8000 pipeline-api
```

---

## Frontend ↔ Backend Integration

When clicking **“Submit Pipeline”** in the frontend:

* Nodes and edges are POSTed to:

  ```
  POST /pipelines/parse
  ```
* Backend returns:

  ```json
  {
    "num_nodes": 4,
    "num_edges": 3,
    "is_dag": true,
    "cycle": null
  }
  ```
* Frontend displays the result as a toast notification

---

## Running Tests

```bash
cd backend
pytest -v
```

With coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

---

## Continuous Integration

CI is configured via **GitHub Actions**:

* Runs on every push & PR to `main`
* Installs dependencies
* Runs full pytest suite with coverage

Workflow file:

```text
.github/workflows/ci.yml
```

---

## Backend API Endpoints

### Health

* `GET /` – Service info
* `GET /health` – Health check

### Pipeline

* `POST /pipelines/parse` – Analyze pipeline DAG

### Monitoring

* `GET /metrics` – Cache stats & config

---

## Architecture Highlights

* Schema-driven frontend nodes (no duplicated components)
* Clean backend layering:

  * Routes → Services → Models
* Business logic isolated from HTTP
* Cache abstraction ready for Redis
* Testable, maintainable, scalable

---

## Future Improvements

* Redis cache
* Auth (JWT / API keys)
* API versioning
* Persistent pipeline storage
* Async workers
* Deployment to Fly.io / AWS / GCP

---

## License

This project is provided for **educational and evaluation purposes**.

---

## Author Notes

This repository demonstrates:

* Frontend abstraction & scalability
* Backend architecture maturity
* Production-grade practices
* Testability & CI readiness

Built with clarity, extensibility, and maintainability in mind.