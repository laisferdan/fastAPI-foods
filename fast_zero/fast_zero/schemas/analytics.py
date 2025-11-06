from datetime import datetime, timedelta, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


DEFAULT_DAYS = 7


class AnalyticsParams(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tz: Optional[str] = Field(default="UTC", description="Timezone name, e.g., UTC or America/Sao_Paulo")

    @model_validator(mode="after")
    def validate_and_default_dates(self):
        start = self.start_date
        end = self.end_date

        if start is None and end is None:
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=DEFAULT_DAYS)
        elif start is None and end is not None:
            start = end - timedelta(days=DEFAULT_DAYS)
        elif start is not None and end is None:
            end = start + timedelta(days=DEFAULT_DAYS)

        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        if start > end:
            raise ValueError("start_date must be before or equal to end_date")

        self.start_date = start
        self.end_date = end
        return self


class SummaryOut(BaseModel):
    total_kcal: int
    total_meals: int
    total_foods: int


class SeriesPoint(BaseModel):
    date: datetime
    kcal: int


class CaloriesByDayOut(BaseModel):
    points: List[SeriesPoint]
    total_days: int


class DistributionItem(BaseModel):
    tipo_refeicao: str
    kcal: int
    percent: float


class DistributionByMealOut(BaseModel):
    items: List[DistributionItem]
