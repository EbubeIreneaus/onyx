import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from setting import settings
from fastapi import HTTPException, status

def encode(data: dict) -> str:
    alg = settings.JWT_ALGORITHM or "HS256"
    token = jwt.encode(data, settings.JWT_SECRET, algorithm=alg)
    return token

def decode(token: str) -> dict:
    alg = settings.JWT_ALGORITHM or "HS256"
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=[alg])
        return data
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
