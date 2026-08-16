"""
main.py
--------
FastAPI application entry point.

Run with (from inside backend/):
    uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import health, timer, sessions
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
app.include_router(timer.router)
app.include_router(sessions.router)

# --- Frontend: static files + templates ---
# Paths are built from this file's own location (not the current working
# directory), so this works whether you run uvicorn from backend/ or from
# the project root with --app-dir backend.
BACKEND_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))


@app.get("/")
def serve_dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"active": "dashboard"})


@app.get("/timer")
def serve_timer(request: Request):
    return templates.TemplateResponse(request, "timer.html", {"active": "timer"})


@app.get("/mentor")
def serve_mentor(request: Request):
    return templates.TemplateResponse(request, "mentor.html", {"active": "mentor"})


@app.get("/analytics")
def serve_analytics(request: Request):
    return templates.TemplateResponse(request, "analytics.html", {"active": "analytics"})


@app.get("/reports")
def serve_reports(request: Request):
    return templates.TemplateResponse(request, "reports.html", {"active": "reports"})
