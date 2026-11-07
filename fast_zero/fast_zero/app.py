from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fast_zero.routes import (
    analytics,
    auth,
    recipes,
    recommendations,
    records,
    users,
)
from fast_zero.schemas.users import Message
from fast_zero.settings.settings import Settings

app = FastAPI(
    title='API Comida - Rangos Week',
    description='API Univesp',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings().CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recipes.router)
app.include_router(records.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
