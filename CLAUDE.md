# CLAUDE.md - Congress.dev AI Assistant Guide

## Project Overview

Congress.dev is a full-stack application that parses, analyzes, and visualizes US Congressional legislation. It ingests US Code XML and bill data from govinfo.gov, parses legislative actions, predicts codification changes, and presents diffs between current and predicted US Code. The production site is at [congress.dev](https://congress.dev).

## Repository Structure

```
congress-dev/
├── backend/              # Python backend (Flask API, FastAPI API, parser, DB models)
│   ├── congress_api/     # Legacy Flask/Connexion REST API (port 9090)
│   ├── congress_fastapi/ # Modern FastAPI REST API (port 9091 → 8080 internal)
│   ├── congress_parser/  # Core legislation parsing engine
│   ├── congress_db/      # SQLAlchemy ORM models and DB session management
│   └── .alembic/         # Database migrations (Alembic)
├── frontend/             # Legacy React SPA (port 3000) — Blueprint.js, Nivo charts
├── hillstack/            # Modern Next.js 15 app (port 3001) — MUI, tRPC, Prisma
├── .docker/              # Docker Compose configs (dev, prod, local)
├── .github/workflows/    # CI/CD (tests on push, deploy on master)
├── openapi/              # OpenAPI 3.0 specification (congress.yaml)
├── scripts/              # Deployment and data import scripts
└── sql/                  # Reference SQL schema files
```

## Tech Stack

### Backend (Python)
- **Flask API** (`congress_api`): Legacy REST API using Connexion + OpenAPI spec
- **FastAPI** (`congress_fastapi`): Modern async API with 8 route modules
- **SQLAlchemy ~1.4**: ORM with PostgreSQL (psycopg2-binary)
- **Alembic**: Database migrations (`backend/.alembic/`)
- **Parsing**: lxml for XML, spacy for NLP, litellm for LLM integration, chromadb for vector search
- **Python version**: 3.13 in Docker, CI runs on 3.9

### Frontend — Legacy (`frontend/`)
- React 18, React Router v5, react-scripts (CRA with react-app-rewired)
- Blueprint.js v5 for UI components
- Nivo v0.88 for data visualization charts
- Prettier for formatting (tabWidth: 4, double quotes, semicolons)

### Frontend — Modern (`hillstack/`)
- Next.js 15 with Turbopack, React 19, TypeScript
- MUI v7 for UI components
- tRPC v11 + TanStack React Query for type-safe API calls
- Prisma 7 ORM (mirrors backend DB)
- NextAuth v5 (beta) for authentication (Google OAuth)
- Biome for linting/formatting (indent: 4, single quotes)
- Package manager: **pnpm** (10.18.2)

### Database
- PostgreSQL 16
- Database name: `us_code_2025`
- Default credentials (dev): `parser`/`parser`

### Infrastructure
- Docker Compose for local development and production
- Self-hosted GitHub Actions runner for CI/CD
- Deployment: push to `master` triggers build and deploy

## Common Commands

### Backend

```bash
# Setup virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Run Flask API
python3 -m congress_api

# Run FastAPI
uvicorn congress_fastapi.app:app --host 0.0.0.0 --port 8080

# Run tests
cd backend && pytest congress_parser

# Import data
python3 -m congress_parser.importers.releases   # US Code releases
python3 -m congress_parser.importers.bills       # Bill data

# Run Alembic migrations
cd backend && alembic upgrade head
```

### Frontend (Legacy)

```bash
cd frontend
yarn install
yarn start       # Dev server on port 3000
yarn build       # Production build
yarn test        # Run tests
yarn format      # Prettier formatting
```

### Hillstack (Modern Frontend)

```bash
cd hillstack
pnpm install
pnpm dev           # Dev server on port 3001 (Turbopack)
pnpm build         # Production build
pnpm typecheck     # TypeScript type checking
pnpm check         # Biome lint + format check
pnpm check:write   # Biome auto-fix
pnpm db:generate   # Prisma migrate dev
pnpm db:migrate    # Prisma migrate deploy
pnpm db:push       # Push schema to DB
pnpm db:studio     # Open Prisma Studio
```

### Docker

```bash
# Full development stack
docker-compose -f .docker/docker-compose.yml up -d

# Local frontend with remote API (api.congress.dev)
bash scripts/start_local.sh

# Production build and deploy
docker-compose -f .docker/docker-compose.yml -f .docker/docker-compose.prod.yml build
bash scripts/start_prod.sh
```

## Code Style and Conventions

### Python (Backend)
- **Linter**: Flake8 with max line length 88, max complexity 18
- **Ignored rules**: E501, Q000, D103, D100, D101, D102, D107, Q002, D205, D400, E203, E266, W503
- Follow existing patterns in each module — Flask API uses Connexion controllers, FastAPI uses routers with dependency injection
- Database models live in `congress_db/models.py` using SQLAlchemy declarative base
- FastAPI route pattern: `congress_fastapi/routes/<domain>.py` → `congress_fastapi/handlers/<domain>.py` → `congress_fastapi/db/<domain>.py`

### JavaScript/TypeScript (Hillstack)
- **Formatter/Linter**: Biome (replaces ESLint + Prettier)
- Indent width: 4 spaces
- Single quotes in JS/JSX
- Import organization: auto-sorted by Biome
- Path alias: `~/` maps to `src/`
- TypeScript strict mode enabled
- All server-side code in `src/server/`; tRPC routers in `src/server/api/`

### JavaScript (Legacy Frontend)
- **Formatter**: Prettier (tabWidth: 4, double quotes, semicolons, trailing commas)
- Path aliases configured in `jsconfig.json` for components, context, pages, styles

## Architecture Notes

### Dual API Design
The backend has two API implementations sharing the same database:
- `congress_api` (Flask): Legacy, runs on port 9090, uses Connexion with OpenAPI spec
- `congress_fastapi` (FastAPI): Modern replacement, runs on port 8080 (mapped to 9091), has 8 route modules: members, legislation, legislation_version, search, user, stats, uscode, committees

Both import models from `congress_db` and use the same PostgreSQL database.

### Dual Frontend Design
The project is migrating from the legacy React SPA to a modern Next.js app:
- `frontend/`: Legacy CRA app (Blueprint.js), port 3000, talks to Flask API
- `hillstack/`: Modern Next.js 15 app (MUI + tRPC + Prisma), port 3001, talks directly to DB via Prisma and to APIs via tRPC

### Parser Pipeline (`congress_parser`)
The core parsing engine has three main processes:
1. **US Code Parsing**: Converts ~600MB+ XML from govinfo.gov into a hierarchical tree structure
2. **Legislation Parsing**: Downloads bills, parses amendment actions, predicts codification changes
3. **Diff Generation**: Computes diffs between current US Code and predicted changes from bills

Key modules:
- `importers/`: Data ingestion (releases, bills)
- `actions/`: Legislative action parsing and application
- `appropriations/`: Federal spending analysis
- `bioguide/`: Legislator biographical data
- `prompt_runners/`: LLM-based analysis integration
- `run_through.py`: Main orchestration
- `compare.py`: Diff computation

### Database Schema
Multi-schema PostgreSQL design (see `hillstack/prisma/schema.prisma` for full schema):
- **public**: Core legislation, versions, content, actions, votes, legislators, committees
- **appropriations**: Federal spending data
- **authentication**: User accounts and sessions
- **prompts**: LLM prompt management and batch results
- **sensitive**: User-specific data (bill tracking, LLM queries)

Key enums (from `congress_db/models.py`):
- `LegislationType`: hr, s, hjres, sjres, hconres, sconres, hres, sres
- `LegislationChamber`: house, senate
- `LegislationVersionEnum`: ih, rh, rs, eh, es, enr, etc. (bill version stages)

## Environment Variables

### Backend
| Variable | Default | Description |
|----------|---------|-------------|
| `db_user` | `parser` | PostgreSQL username |
| `db_pass` | `parser` | PostgreSQL password |
| `db_table` | `us_code_2025` | Database name |
| `db_host` | `0.0.0.0:5432` | Database host:port |
| `STAGE` | `dev` | Environment (dev/prod) |
| `PORT` | `9090` | API port |
| `CACHE_HEADER_TIME` | `0` | HTTP cache header duration |

### Hillstack
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `NODE_ENV` | development/production |
| `NEXT_PUBLIC_APP_URL` | Frontend URL |
| `NEXTAUTH_URL` | NextAuth callback URL |
| `AUTH_SECRET` | NextAuth secret |
| `GOOGLE_CLIENT_ID` | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret |

### Legacy Frontend
| Variable | Description |
|----------|-------------|
| `REACT_APP_API_URL` | Backend API URL (Flask) |
| `REACT_APP_API_V2_URL` | Backend API URL (FastAPI) |

## Testing

- **Framework**: pytest
- **Test location**: `backend/congress_parser/tests/`
- **Test files**: `test_actions.py`, `test_cite_parser.py`, `test_parser.py`
- **Config**: `backend/pytest.ini` (pythonpath = congress_parser)
- **Run**: `cd backend && pytest congress_parser`
- **CI**: Runs on every push via GitHub Actions (`.github/workflows/tests.yml`)

## CI/CD Pipeline

1. **Tests** (`.github/workflows/tests.yml`): Runs on every push to any branch. Sets up Python 3.9 venv, installs from `requirements.txt`, runs `pytest congress_parser`.
2. **Deploy** (`.github/workflows/deploy.yml`): Triggers on push to `master`. Pulls latest code, builds Docker containers with production compose overlay, runs `scripts/start_prod.sh`.

## Key Files for Common Tasks

| Task | Files |
|------|-------|
| Add a new API endpoint (FastAPI) | `backend/congress_fastapi/routes/`, `handlers/`, `db/`, `models/` |
| Add a new API endpoint (Flask) | `backend/congress_api/controllers/`, `openapi/congress.yaml` |
| Modify DB schema | `backend/congress_db/models.py`, `backend/.alembic/`, `hillstack/prisma/schema.prisma` |
| Add a new page (Next.js) | `hillstack/src/app/<route>/page.tsx` |
| Add a new page (React) | `frontend/src/pages/` |
| Add a tRPC router | `hillstack/src/server/api/` |
| Modify parsing logic | `backend/congress_parser/actions/`, `run_through.py` |
| Add new data importer | `backend/congress_parser/importers/` |
| Update Docker config | `.docker/docker-compose.yml` |
