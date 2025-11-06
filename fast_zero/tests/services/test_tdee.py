import math

import pytest

from fast_zero.fast_zero.services.tdee import Profile, bmr_mifflin_st_jeor, tdee


def test_bmr_male():
    p = Profile(sexo='M', idade=30, peso_kg=70, altura_cm=175, nivel_atividade=1.55)
    b = bmr_mifflin_st_jeor(p)
    assert 1600 < b < 1750


def test_bmr_female():
    p = Profile(sexo='F', idade=30, peso_kg=60, altura_cm=165, nivel_atividade=1.375)
    b = bmr_mifflin_st_jeor(p)
    assert 1300 < b < 1500


def test_tdee():
    p = Profile(sexo='M', idade=25, peso_kg=80, altura_cm=180, nivel_atividade=1.725)
    total = tdee(p)
    assert total > 0
    assert math.isfinite(total)
