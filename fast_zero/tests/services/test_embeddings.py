import math

from fast_zero.fast_zero.services.embeddings import (
    normalize_min_max,
    kcal_vector2d,
    cosine_similarity,
)


def test_normalize_min_max_basic():
    assert normalize_min_max(50, 0, 100) == 0.5
    assert normalize_min_max(0, 0, 100) == 0.0
    assert normalize_min_max(100, 0, 100) == 1.0


def test_kcal_vector2d_shapes_and_bounds():
    vx = kcal_vector2d(200, 0, 400)
    assert len(vx) == 2
    assert 0.0 <= vx[0] <= 1.0
    assert math.isclose(sum(vx), 1.0, rel_tol=1e-6)


def test_cosine_similarity():
    a = (1.0, 0.0)
    b = (1.0, 0.0)
    c = (0.0, 1.0)
    assert math.isclose(cosine_similarity(a, b), 1.0, rel_tol=1e-6)
    assert math.isclose(cosine_similarity(a, c), 0.0, rel_tol=1e-6)
