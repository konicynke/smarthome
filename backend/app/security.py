import hmac
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import API_KEY, JWT_EXPIRE_MINUTES, JWT_SECRET

JWT_ALGORITHM = "HS256"
MAX_PASSWORD_BYTES = 72

_bearer = HTTPBearer(auto_error=False)
_dummy_hash = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt())


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, password_hash):
    encoded = password.encode()
    if len(encoded) > MAX_PASSWORD_BYTES:
        return False
    return bcrypt.checkpw(encoded, password_hash.encode())


def burn_password_check(password):
    """Spend the same time as a real check when the user does not exist."""
    encoded = password.encode()[:MAX_PASSWORD_BYTES]
    bcrypt.checkpw(encoded, _dummy_hash)


def create_token(username):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")


def require_user(credentials: HTTPAuthorizationCredentials = Depends(_bearer)):
    username = decode_token(credentials.credentials) if credentials else None
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


def require_api_key(x_api_key: str = Header(default="")):
    if not hmac.compare_digest(x_api_key.encode(), API_KEY.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
