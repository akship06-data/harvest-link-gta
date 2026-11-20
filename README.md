# HarvestLink GTA — Hyper-Local Surplus Food Rescue & Pantry Router

**Status:** Portfolio / engineering demo project. Seeded with fictional Toronto pilot data and not currently connected to real food donors or shelters.

Walking along the **Yonge–Dundas Square, Victoria Street, and Downtown Toronto core**, visible food insecurity and unhoused neighbors sit steps away from campus events, cafes, and independent grocers discarding untouched catered trays and end-of-day surplus.

**HarvestLink GTA** is a full-stack prototype exploring how hyper-local coordination could close that last-mile gap within a 5 km Downtown Toronto / Dundas corridor radius—matching commercial and campus event surplus with local drop-in centres, community fridges, and student food pantries before food spoils.

---

## Context & Existing Ecosystem

Large-scale food recovery in Toronto is already led by established organizations such as **Second Harvest** (and its **FoodRescue.ca** platform) and **Feed It Forward**.

This project was built as a learning exercise in geospatial matching, state-machine workflows, and domain-informed input validation—focused specifically on small-batch, same-day campus and neighborhood surplus (e.g., untouched event catering trays) rather than commercial grocery logistics.

---

* **Merchant Intake App (Shopify Embedded App — Real Working Code):** Built an embedded Shopify Admin app (`shopify-merchant-app/`) using React Router, TypeScript, and Polaris Web Components that queries live store inventory via the Shopify Admin GraphQL API and executes `tagsAdd` / `metafieldsSet` mutations to flag near-expiry items (`< 24h`) for pickup.

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
