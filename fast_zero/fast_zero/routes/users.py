from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database.database import get_session
from fast_zero.models.models import (
    ConsumptionLog,
    RecommendationFeedback,
    User,
    UserProfile,
)
from fast_zero.schemas.users import (
    Message,
    UserPublic,
    UserSchema,
    UserUpdate,
)
from fast_zero.security.auth import get_current_user
from fast_zero.security.passwords import get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def _ensure_unique(
    session: Session,
    *,
    username: str | None,
    email: str | None,
    exclude_id: int | None = None,
) -> None:
    if username is not None:
        found = session.scalar(select(User).where(User.username == username))
        if found and found.id != exclude_id:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
    if email is not None:
        found = session.scalar(select(User).where(User.email == email))
        if found and found.id != exclude_id:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )


def _commit_or_conflict(
    session: Session,
    *,
    username: str | None,
    email: str | None,
    exclude_id: int | None = None,
) -> None:
    """Commit; uma corrida entre dois pedidos vira 409 em vez de 500."""
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        _ensure_unique(
            session, username=username, email=email, exclude_id=exclude_id
        )
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists'
        ) from None


@router.post('', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: DbSession):
    email = user.email.lower()
    _ensure_unique(session, username=user.username, email=email)

    db_user = User(
        username=user.username,
        email=email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    _commit_or_conflict(session, username=user.username, email=email)
    session.refresh(db_user)
    return db_user


@router.get('/me', response_model=UserPublic)
def read_me(current_user: CurrentUser):
    return current_user


@router.put('/me', response_model=UserPublic)
def update_me(user: UserUpdate, current_user: CurrentUser, session: DbSession):
    email = user.email.lower() if user.email else None
    _ensure_unique(
        session,
        username=user.username,
        email=email,
        exclude_id=current_user.id,
    )

    if user.username is not None:
        current_user.username = user.username
    if email is not None:
        current_user.email = email
    if user.password is not None:
        current_user.password = get_password_hash(user.password)

    _commit_or_conflict(
        session,
        username=user.username,
        email=email,
        exclude_id=current_user.id,
    )
    session.refresh(current_user)
    return current_user


@router.delete('/me', response_model=Message)
def delete_me(current_user: CurrentUser, session: DbSession):
    # O SQLite não aplica ON DELETE CASCADE por padrão.
    for model in (ConsumptionLog, RecommendationFeedback, UserProfile):
        session.execute(delete(model).where(model.user_id == current_user.id))
    session.delete(current_user)
    session.commit()
    return {'message': 'User deleted'}
