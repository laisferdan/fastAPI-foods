from dataclasses import dataclass


@dataclass
class Profile:
    sexo: str  # 'M'|'F'|'O'
    idade: int
    peso_kg: float
    altura_cm: float
    nivel_atividade: float


def bmr_mifflin_st_jeor(profile: Profile) -> float:
    s = profile.sexo.upper()
    if s == 'M':
        base = 5
    else:
        base = -161
    return 10 * profile.peso_kg + 6.25 * profile.altura_cm - 5 * profile.idade + base


def tdee(profile: Profile) -> float:
    return bmr_mifflin_st_jeor(profile) * profile.nivel_atividade
