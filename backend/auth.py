import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import database
from database import hash_password, verify_password

logger = logging.getLogger("uvicorn.error")

# Read JWT Secret from environment with dev-only fallback + warning logging
JWT_SECRET_ENV = os.getenv("JWT_SECRET") or os.getenv("HEATSHIELD_JWT_SECRET")
if JWT_SECRET_ENV:
    SECRET_KEY = JWT_SECRET_ENV
else:
    SECRET_KEY = "DEV_ONLY_SECRET_CHANGE_IN_PRODUCTION_KEY_2026"
    logger.warning("WARNING: JWT_SECRET environment variable is unset! Using dev-only fallback secret key. Do NOT use in production.")

ALGORITHM = "HS256"
DEFAULT_EXPIRE_DAYS = 7
AUTHORITY_REGISTRATION_CODE = os.getenv("AUTHORITY_REGISTRATION_CODE", "HEATSHIELD_AUTH_SECRET_2026")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=DEFAULT_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = int(user_id_raw)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = database.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_dict = dict(user)
    if not user_dict.get("is_active", 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return user_dict


def require_citizen(current_user: dict = Depends(get_current_user)) -> dict:
    role = str(current_user.get("role", "")).lower()
    if role not in ["citizen", "authority"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Citizen role required for this action"
        )
    return current_user


def require_authority(current_user: dict = Depends(get_current_user)) -> dict:
    role = str(current_user.get("role", "")).lower()
    if role != "authority":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Authority privileges required"
        )
    return current_user
