import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# ── Single hardcoded user ─────────────────────────────────────────────
def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

_USER = {
    "name":          "Uirá Peixoto",
    "email":         "uira.peixoto@gmail.com",
    "password_hash": _sha256("Senha@123"),
}

# ── In-memory session store {token: expires_at} ───────────────────────
_sessions: dict[str, datetime] = {}

COOKIE_NAME  = "ws_session"
SESSION_DAYS = 30


def get_current_user(request: Request) -> dict:
    """FastAPI dependency — raises 401 if session is missing or expired."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    expires = _sessions.get(token)
    if not expires or expires < datetime.utcnow():
        _sessions.pop(token, None)
        raise HTTPException(status_code=401, detail="Sessão expirada")
    return _USER


# ── Endpoints ─────────────────────────────────────────────────────────

class LoginIn(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(data: LoginIn, response: Response):
    hashed = _sha256(data.password)
    if (
        data.email.lower() != _USER["email"]
        or not secrets.compare_digest(hashed, _USER["password_hash"])
    ):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    token   = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(days=SESSION_DAYS)
    _sessions[token] = expires

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_DAYS * 86_400,
        # secure=True  # habilitar com HTTPS em produção
    )
    return {"name": _USER["name"], "email": _USER["email"]}


@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        _sessions.pop(token, None)
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {"name": user["name"], "email": user["email"]}
