from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database.database import get_session
from fast_zero.models.models import User
from fast_zero.schemas.users import Token
from fast_zero.security.auth import create_access_token
from fast_zero.security.passwords import verify_password

router = APIRouter(prefix='/auth', tags=['auth'])

FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
DbSession = Annotated[Session, Depends(get_session)]


@router.post('/token', response_model=Token)
def login_for_access_token(form_data: FormData, session: DbSession):
    user = session.scalar(
        select(User).where(User.email == form_data.username.strip().lower())
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {
        'access_token': create_access_token(user.id),
        'token_type': 'bearer',
    }
