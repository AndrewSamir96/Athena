from app.core.security import decode_token
from app.database import get_db
from app.models import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
db_dependency = Depends(get_db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = db_dependency,
) -> User:
    print("[deps.get_current_user] resolving token")
    try:
        user_id = decode_token(token)
    except JWTError:
        print("[deps.get_current_user] invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    user = db.get(User, user_id)
    if user is None:
        print(f"[deps.get_current_user] user not found user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    print(f"[deps.get_current_user] authenticated user_id={user.id}")
    return user
