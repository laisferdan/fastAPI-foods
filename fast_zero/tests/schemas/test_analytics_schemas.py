from datetime import datetime, timedelta, timezone

import pytest

from fast_zero.schemas.analytics import (
    AnalyticsParams,
    CaloriesByDayOut,
    DistributionByMealOut,
    SeriesPoint,
    SummaryOut,
)


def test_analytics_params_defaults_last_7_days():
    params = AnalyticsParams()
    assert params.start_date.tzinfo is not None
    assert params.end_date.tzinfo is not None
    delta = params.end_date - params.start_date
    assert timedelta(days=6) <= delta <= timedelta(days=8)


def test_analytics_params_with_only_end_sets_start_before():
    end = datetime.now(timezone.utc)
    params = AnalyticsParams(end_date=end)
    assert params.start_date < params.end_date


def test_analytics_params_with_only_start_sets_end_after():
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    params = AnalyticsParams(start_date=start)
    assert params.end_date > params.start_date


def test_analytics_params_enforces_order():
    start = datetime(2025, 1, 2, tzinfo=timezone.utc)
    end = datetime(2025, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        AnalyticsParams(start_date=start, end_date=end)


def test_schema_models_serialization_examples():
    s = SummaryOut(total_kcal=1000, total_meals=3, total_foods=3)
    assert s.total_kcal == 1000

    pt = SeriesPoint(date=datetime(2025, 1, 1, tzinfo=timezone.utc), kcal=500)
    out_series = CaloriesByDayOut(points=[pt], total_days=1)
    assert out_series.total_days == 1
    assert out_series.points[0].kcal == 500

    dist = DistributionByMealOut(items=[{"tipo_refeicao": "almoço", "kcal": 600, "percent": 60.0}])
    assert dist.items[0].percent == 60.0
