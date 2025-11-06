from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.routes import recipes, users
from fast_zero.routes import recommendations
from fast_zero.routes import analytics
from fast_zero.schemas.users import Message

app = FastAPI(
    prefix='/teste',
    title='API Comida - Rangos Week',
    description='API Univesp',
)

database = []  


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


app.include_router(recipes.router)
app.include_router(users.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
