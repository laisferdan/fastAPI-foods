from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.orm import Session

from fast_zero.database.database import get_session
from fast_zero.models.models import User
from fast_zero.settings.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )


def create_access_token(
    subject: str | int, expires_minutes: int | None = None
) -> str:
    settings = Settings()
    minutes = (
        settings.ACCESS_TOKEN_EXPIRE_MINUTES
        if expires_minutes is None
        else expires_minutes
    )
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(subject),
        'iat': now,
        'exp': now + timedelta(minutes=minutes),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> int:
    settings = Settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'require': ['exp', 'sub']},
        )
        return int(payload['sub'])
    except (PyJWTError, ValueError) as exc:
        raise _credentials_exception() from exc


def get_current_user(
    user_id: Annotated[int, Depends(get_current_user_id)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise _credentials_exception()
    return user
