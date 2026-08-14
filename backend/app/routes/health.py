"""
routes/health.py
------------------
Simple health check endpoint to confirm the API is up and reachable.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "running"}