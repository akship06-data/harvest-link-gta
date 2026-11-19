# HarvestLink GTA — Hyper-Local Surplus Food Rescue & Pantry Router

Walking along the **Yonge–Dundas Square, Victoria Street, and Downtown Toronto core**, visible food insecurity and unhoused neighbors sit steps away from campus events, cafes, and independent grocers discarding untouched catered trays and end-of-day surplus.

**HarvestLink GTA** closes that last-mile coordination gap within a 5 km Downtown Toronto / Dundas corridor radius—matching verified commercial and campus event food surplus with local drop-in centres, community fridges, and student food pantries before food spoils.

## Engineering & Regulatory Architecture

* **Ontario *Donation of Food Act, 1994* & DineSafe Guardrails (`Pydantic` + `FastAPI`):** Enforces strict intake validation—rejecting unverified residential leftovers and automatically blocking perishable listings with fewer than 2 hours remaining before their cold-chain/best-before cutoff.
* **Constraint-Based Geospatial Matching Engine (`Python` + `PostgreSQL`):** Pairs surplus food batches with receiving shelters/pantries using Haversine proximity routing, refrigeration compatibility checks, and dietary tag alignment (`Vegetarian`, `Halal`, `Nut-Free`, `Shelf-Stable`).
* **Chain-of-Custody Audit Trail (`SQLAlchemy`):** Tracks every transfer across four immutable states (`AVAILABLE -> CLAIMED -> PICKED_UP -> DELIVERED`) with food-safety packaging verification timestamps.
* **Mobile-First Volunteer & Coordinator Dispatch UI (`React` + `TypeScript` + `Tailwind CSS`):** Enables donors to log surplus batches, pantries to filter compatible incoming food, and volunteer couriers to claim nearby Dundas/Downtown pickups.
* **Automated Test Coverage (`pytest`):** Unit tests verifying expiry cutoffs, dietary/cold-chain filtering, and Haversine distance ranking.

## Tech Stack

* **Backend:** Python 3.11, FastAPI, SQLAlchemy, Pydantic, pytest
* **Frontend:** React 18, TypeScript, Tailwind CSS, Vite
* **Database & Infrastructure:** PostgreSQL 16 (with local SQLite fallback), Docker, Docker Compose

## Quick Start

### 1. Run Backend + PostgreSQL via Docker
```bash
docker-compose up --build
```
Interactive API documentation is available at `http://localhost:8000/docs`.

### 2. Run Backend & Test Suite Locally (Without Docker)
```bash
cd backend
pip install -r requirements.txt
pytest
python seed.py
uvicorn app.main:app --reload
```

### 3. Run Frontend Locally
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` to view the Downtown Toronto / Dundas corridor dispatch board.

## Deployment (Render + Vercel)
* **Backend (Render):** Root directory `backend`, Build command `pip install -r requirements.txt && python seed.py`, Start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
* **Frontend (Vercel):** Root directory `frontend`, Environment Variable `VITE_API_URL=https://<your-render-service>.onrender.com/api`.
