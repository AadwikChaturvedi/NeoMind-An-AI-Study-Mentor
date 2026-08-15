"""
main.py
--------
FastAPI application entry point.

Run with (from inside backend/):
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health
from app.database import init_db

app = FastAPI(title="NeoMind AI")


@app.on_event("startup")
def on_startup():
    init_db()

# --- CORS ---
# Allows the frontend (running on a different origin/port during dev)
# to call this API. Tighten allow_origins before deploying to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
# Each feature gets its own router (modular structure).
# Add new ones the same way as you build them out:
#   from app.routes import dashboard
#   app.include_router(dashboard.router)
app.include_router(health.router)
