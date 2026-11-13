from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, SecretStr
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.auth.cookies import clear_session_files
from app.auth.instagram import sign_in, sign_out
from app.auth.sessions import assert_origin, public_state, sessions
from app.config import get_settings
from app.errors import ApiError, unsupported
from app.security.turnstile import client_key, verify_turnstile

router = APIRouter()


class LoginBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=64)
    password: SecretStr
    turnstile_token: str | None = None


class VerifyBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=64)
    challenge_id: str = Field(min_length=8, max_length=80)
    code: str = Field(min_length=4, max_length=12)
    turnstile_token: str | None = None


def _enabled() -> None:
    if not get_settings().enable_instagram_login:
        raise unsupported("Instagram sign-in is turned off on this server.")


def _agent(request: Request) -> str:
    return request.headers.get("user-agent", "")[:300]


@router.get("/api/auth/session")
async def read_session(request: Request) -> dict:
    return public_state(request)


@router.post("/api/auth/instagram/login")
async def login(request: Request, body: LoginBody):
    assert_origin(request)
    _enabled()
    await verify_turnstile(body.turnstile_token, request)
    ip_key = f"ip:{client_key(request)}"
    name_key = f"user:{body.username.strip().lower()}"
    if not sessions.allow_attempt(ip_key) or not sessions.allow_attempt(name_key):
        raise ApiError("busy", "Too many sign-in attempts. Wait and try again.", 429)
    result = await sign_in(body.username.strip(), body.password.get_secret_value(), None, None, _agent(request))
    if result["status"] == "two_factor":
        return {"status": "two_factor", "challenge_id": result["challenge_id"]}
    token = sessions.open_session(username=result["username"], settings_dict=result["settings"], user_agent=_agent(request))
    response = JSONResponse({"status": "ok", "username": result["username"]})
    sessions.write_cookie(response, token)
    return response


@router.post("/api/auth/instagram/verify")
async def verify(request: Request, body: VerifyBody):
    assert_origin(request)
    _enabled()
    await verify_turnstile(body.turnstile_token, request)
    result = await sign_in(body.username.strip(), "", body.code.strip(), body.challenge_id, _agent(request))
    token = sessions.open_session(username=result["username"], settings_dict=result["settings"], user_agent=_agent(request))
    response = JSONResponse({"status": "ok", "username": result["username"]})
    sessions.write_cookie(response, token)
    return response


@router.post("/api/auth/logout")
async def logout(request: Request):
    assert_origin(request)
    username, payload, job_ids = sessions.drop(request)
    clear_session_files(job_ids)
    if payload:
        await sign_out(payload)
    response = JSONResponse({"status": "ok", "username": username})
    sessions.clear_cookie(response)
    return response
