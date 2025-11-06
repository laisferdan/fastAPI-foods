import pytest
from pydantic import ValidationError

from fast_zero.fast_zero.schemas.profile import UserProfileIn
from fast_zero.fast_zero.schemas.feedback import FeedbackIn
from fast_zero.fast_zero.schemas.consumptions import ConsumptionIn


def test_profile_validation_ok():
    p = UserProfileIn(sexo='M', idade=28, peso_kg=75.0, altura_cm=180.0, nivel_atividade=1.55)
    assert p.sexo == 'M'

def test_feedback_validation():
    FeedbackIn(recipe_id=1, feedback='like')
    with pytest.raises(ValidationError):
        FeedbackIn(recipe_id=1, feedback='meh')


def test_consumption_defaults():
    c = ConsumptionIn(recipe_id=1, kcal=500, tipo_refeicao='almoço')
    assert c.consumed_at is None
