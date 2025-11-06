from __future__ import annotations

import math
from typing import Tuple


def normalize_min_max(value: float, min_v: float, max_v: float) -> float:
    if max_v <= min_v:
        return 0.0
    x = (value - min_v) / (max_v - min_v)
    return max(0.0, min(1.0, x))


def kcal_vector2d(kcal: float, min_kcal: float, max_kcal: float) -> Tuple[float, float]:
    x = normalize_min_max(kcal, min_kcal, max_kcal)
    return (x, 1.0 - x)


def cosine_similarity(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    ax, ay = a
    bx, by = b
    dot = ax * bx + ay * by
    na = math.sqrt(ax * ax + ay * ay)
    nb = math.sqrt(bx * bx + by * by)
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
