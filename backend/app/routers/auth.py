from fastapi import APIRouter, Depends, HTTPException, status

from app import repository
from app.db import get_conn
from app.schemas import LoginPayload, TokenOut
from app.security import burn_password_check, create_token, verify_password

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginPayload, conn=Depends(get_conn)):
    with conn.cursor() as cur:
        user = repository.get_user(cur, payload.username)
    if user is None:
        burn_password_check(payload.password)
        valid = False
    else:
        valid = verify_password(payload.password, user["password_hash"])
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return TokenOut(access_token=create_token(user["username"]))
