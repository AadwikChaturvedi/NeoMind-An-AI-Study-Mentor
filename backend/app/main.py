"""
main.py
--------
FastAPI application entry point.

Run with (from inside backend/):
    uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

# --- Environment variables ---
# .env lives at the project root (one level up from backend/), not
# inside backend/ itself — so it's loaded from an explicit path built
# from this file's own location, not the current working directory.
# This must happen before importing routes: app/services/gemini_service.py
# reads GEMINI_MODEL at import time, so the .env values need to already
# be in os.environ by then.
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

load_dotenv(PROJECT_ROOT / ".env")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import health, timer, sessions, mentor
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="NeoMind AI", lifespan=lifespan)

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
app.include_router(mentor.router)

# --- Frontend: static files + templates ---
# FRONTEND_DIR was already computed above, from this file's own location
# (not the current working directory) — works whether you run uvicorn
# from backend/ or from the project root with --app-dir backend.
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
