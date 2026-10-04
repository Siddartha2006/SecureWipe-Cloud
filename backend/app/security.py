import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from jwt import InvalidTokenError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User

ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return salt.hex() + "$" + derived.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$", 1)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 310_000).hex()
        return hmac.compare_digest(candidate, expected)
    except (ValueError, TypeError):
        return False


def issue_token(user_id: str) -> str:
    return jwt.encode({"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(hours=12)}, settings.jwt_secret, algorithm=ALGORITHM)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        user_id = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[ALGORITHM]).get("sub")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    return user
