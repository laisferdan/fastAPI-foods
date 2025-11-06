from http import HTTPStatus
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database.database import get_session
from fast_zero.models.models import (
    ConsumptionLog,
    RecommendationFeedback,
    User,
    UserProfile,
)
from fast_zero.schemas.consumptions import ConsumptionIn, ConsumptionOut
from fast_zero.schemas.feedback import FeedbackIn, FeedbackOut
from fast_zero.schemas.profile import UserProfileIn, UserProfileOut
from fast_zero.schemas.recommendations import (
    RecommendationItem,
    RecommendationList,
)
from fast_zero.schemas.users import Message
from fast_zero.services.recommendation_engine import recommend_for_user
from fast_zero.security.auth import get_current_user_id
from loguru import logger

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])


@router.get(
    "/recommend",
    response_model=RecommendationList | Message,
    status_code=HTTPStatus.OK,
)
def get_recommendations(
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    logger.info("Generating recommendations for user_id={} on {}", current_user_id, date.today())
    items = recommend_for_user(session, user_id=current_user_id, on_date=date.today())
    if not items:
        return {"message": "Atualize suas informações pessoais para receber recomendações de refeição."}
    return {"items": [RecommendationItem.model_validate(i.__dict__) for i in items]}


@router.get("/profile", response_model=UserProfileOut | Message)
def get_profile(session: Session = Depends(get_session), current_user_id: int = Depends(get_current_user_id)):
    prof = session.scalar(select(UserProfile).where(UserProfile.user_id == current_user_id))
    if not prof:
        return {"message": "Perfil não encontrado"}
    return UserProfileOut(
        user_id=prof.user_id,
        sexo=prof.sexo,
        idade=prof.idade,
        peso_kg=prof.peso_kg,
        altura_cm=prof.altura_cm,
        nivel_atividade=prof.nivel_atividade,
    )


@router.put("/profile", response_model=UserProfileOut)
def put_profile(
    profile: UserProfileIn = ...,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    user = session.scalar(select(User).where(User.id == current_user_id))
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    prof = session.scalar(select(UserProfile).where(UserProfile.user_id == current_user_id))
    if prof:
        prof.sexo = profile.sexo
        prof.idade = profile.idade
        prof.peso_kg = profile.peso_kg
        prof.altura_cm = profile.altura_cm
        prof.nivel_atividade = profile.nivel_atividade
    else:
        prof = UserProfile(
            user_id=current_user_id,
            sexo=profile.sexo,
            idade=profile.idade,
            peso_kg=profile.peso_kg,
            altura_cm=profile.altura_cm,
            nivel_atividade=profile.nivel_atividade,
        )
        session.add(prof)
    session.commit()
    session.refresh(prof)
    return UserProfileOut(
        user_id=prof.user_id,
        sexo=prof.sexo,
        idade=prof.idade,
        peso_kg=prof.peso_kg,
        altura_cm=prof.altura_cm,
        nivel_atividade=prof.nivel_atividade,
    )


@router.post("/consumptions", response_model=ConsumptionOut, status_code=HTTPStatus.CREATED)
def post_consumption(
    payload: ConsumptionIn = ...,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    user = session.scalar(select(User).where(User.id == current_user_id))
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    log = ConsumptionLog(
        user_id=current_user_id,
        recipe_id=payload.recipe_id,
        kcal=payload.kcal,
        tipo_refeicao=payload.tipo_refeicao,
        consumed_at=payload.consumed_at,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return ConsumptionOut(
        id=log.id,
        user_id=log.user_id,
        recipe_id=log.recipe_id,
        kcal=log.kcal,
        tipo_refeicao=log.tipo_refeicao,
        consumed_at=log.consumed_at,
    )


@router.post("/feedback", response_model=FeedbackOut, status_code=HTTPStatus.CREATED)
def post_feedback(
    payload: FeedbackIn = ...,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    user = session.scalar(select(User).where(User.id == current_user_id))
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    fb = RecommendationFeedback(
        user_id=current_user_id,
        recipe_id=payload.recipe_id,
        feedback=payload.feedback,
    )
    session.add(fb)
    session.commit()
    session.refresh(fb)
    return FeedbackOut(id=fb.id, user_id=fb.user_id, recipe_id=fb.recipe_id, feedback=fb.feedback)
