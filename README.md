# HarvestLink GTA — Hyper-Local Surplus Food Rescue & Pantry Router

**Status:** Portfolio / engineering demo project. Seeded with fictional Toronto pilot data and not currently connected to real food donors or shelters.

Walking along the **Yonge–Dundas Square, Victoria Street, and Downtown Toronto core**, visible food insecurity and unhoused neighbors sit steps away from campus events, cafes, and independent grocers discarding untouched catered trays and end-of-day surplus.

**HarvestLink GTA** is a full-stack prototype exploring how hyper-local coordination could close that last-mile gap within a 5 km Downtown Toronto / Dundas corridor radius—matching commercial and campus event surplus with local drop-in centres, community fridges, and student food pantries before food spoils.

---

## Context & Existing Ecosystem

Large-scale food recovery in Toronto is already led by established organizations such as **Second Harvest** (and its **FoodRescue.ca** platform) and **Feed It Forward**.

This project was built as a learning exercise in geospatial matching, state-machine workflows, and domain-informed input validation—focused specifically on small-batch, same-day campus and neighborhood surplus (e.g., untouched event catering trays) rather than commercial grocery logistics.

---

## What’s Real vs. Simulated

* **Status & Data (Simulated):** Pre-seeded with realistic fictional donor and pantry profiles around Yonge–Dundas and TMU (`backend/seed.py`) so the dispatch workflow can be tested out of the box.
* **Geospatial Routing (Simulated / Straight-Line):** Calculates Haversine great-circle distance (`backend/app/matching.py`) rather than live street-network walking, transit, or driving routes.
* **Food-Safety & Liability Guardrails (Modeled, Not Legal Compliance):** Input rules in `backend/app/schemas.py` are *informed by* Ontario's *Donation of Food Act, 1994* (S.O. 1994, c. 19) and Toronto Public Health DineSafe concepts—requiring sealed/commercial-source attestation and enforcing a minimum 2-hour window before expiration. This is a technical modeling exercise, not legal or public-health certification.
* **Backend, State Machine & Tests (Real Working Code):** Full FastAPI REST API, SQLAlchemy persistence, four-stage chain-of-custody tracking (`AVAILABLE -> CLAIMED -> PICKED_UP -> DELIVERED`), React + TypeScript dispatch UI, and automated `pytest` integration tests.

---

## Tech Stack

* **Backend:** Python 3.11, FastAPI, SQLAlchemy, Pydantic, pytest
* **Frontend:** React 18, TypeScript, Tailwind CSS, Vite
* **Database & Infrastructure:** PostgreSQL 16 (with local SQLite fallback), Docker, Docker Compose

---

## Quick Start

### 1. Run Backend & Test Suite Locally
```bash
cd backend
pip install -r requirements.txt
pytest
python seed.py
uvicorn app.main:app --reload
