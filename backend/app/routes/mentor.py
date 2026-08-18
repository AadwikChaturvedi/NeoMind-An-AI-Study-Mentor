"""
routes/mentor.py
--------------------
AI Mentor chat endpoint. Delegates the actual Gemini call to
services/gemini_service.py and turns any failure into a clean HTTP
error response instead of a raw 500 with a stack trace.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.mentor import MentorChatRequest, MentorChatResponse
from app.services.gemini_service import ask_mentor, GeminiServiceError

router = APIRouter(prefix="/mentor", tags=["AI Mentor"])


@router.post("/chat", response_model=MentorChatResponse)
def chat_with_mentor(payload: MentorChatRequest):
    try:
        reply = ask_mentor(payload.message)
    except GeminiServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return MentorChatResponse(reply=reply)
