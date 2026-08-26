from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

ALGORITMO = "HS256"

_bearer_scheme = HTTPBearer(auto_error=False)


def crear_token_admin() -> str:
    expiracion = datetime.now(timezone.utc) + timedelta(hours=settings.ADMIN_TOKEN_EXPIRA_HORAS)
    payload = {"sub": "admin", "exp": expiracion}
    return jwt.encode(payload, settings.ADMIN_SECRET_KEY, algorithm=ALGORITMO)


def obtener_admin_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
):
    """
    Dependencia para proteger los endpoints administrativos (crear empresas,
    rutas, horarios, etc.). Requiere el header: Authorization: Bearer <token>,
    obtenido desde POST /admin/login.
    """
    if credenciales is None:
        raise HTTPException(status_code=401, detail="No autenticado")
    try:
        jwt.decode(credenciales.credentials, settings.ADMIN_SECRET_KEY, algorithms=[ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sesión expirada, inicia sesión de nuevo")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    return True
