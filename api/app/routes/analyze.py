from __future__ import annotations

from fastapi import APIRouter, Request

from app.models import AnalyzeRequest, AnalyzeResult
from app.security.ratelimit import limit_value, limiter
from app.security.turnstile import verify_turnstile
from app.auth.sessions import session_hash, sessions
from app.services.analyze import analyze_url

router = APIRouter()


@router.post("/api/analyze", response_model=AnalyzeResult)
@limiter.limit(limit_value)
async def analyze(request: Request, body: AnalyzeRequest) -> AnalyzeResult:
    await verify_turnstile(body.turnstile_token, request)
    bound = session_hash(request)
    instagram_settings = sessions.instagram_settings(request) if bound else None
    return await analyze_url(body.url, bound, instagram_settings)
