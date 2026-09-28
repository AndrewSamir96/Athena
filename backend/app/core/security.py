from datetime import datetime, timedelta, timezone

import bcrypt
from app.config import settings
from jose import jwt

MAX_BCRYPT_PASSWORD_BYTES = 72


def _password_bytes(password: str) -> bytes:
    encoded = password.encode("utf-8")
    if len(encoded) > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError("Password must be at most 72 bytes when encoded as UTF-8")
    return encoded


def hash_password(password: str) -> str:
    print("[security.hash_password] hashing password")
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    result = bcrypt.checkpw(_password_bytes(plain), hashed.encode("ascii"))
    print(f"[security.verify_password] valid={result}")
    return result


def create_access_token(user_id: str) -> str:
    print(f"[security.create_access_token] user_id={user_id}")
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> str:
    """Returns the user_id from a valid token, raises jose.JWTError if invalid/expired."""
    print("[security.decode_token] decoding token")
    payload = jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    user_id = payload["sub"]
    print(f"[security.decode_token] user_id={user_id}")
    return user_id
