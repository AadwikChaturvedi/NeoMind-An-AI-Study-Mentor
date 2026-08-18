"""
schemas/mentor.py
--------------------
Request/response schemas for the AI Mentor chat endpoint.
"""

from pydantic import BaseModel


class MentorChatRequest(BaseModel):
    message: str


class MentorChatResponse(BaseModel):
    reply: str
