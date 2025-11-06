from pydantic import BaseModel, Field, PositiveInt


class FeedbackIn(BaseModel):
    recipe_id: PositiveInt
    feedback: str = Field(pattern=r"^(like|dislike)$")
    model_config = {
        "json_schema_extra": {
            "example": {"recipe_id": 1, "feedback": "like"}
        }
    }


class FeedbackOut(FeedbackIn):
    id: int
    user_id: int
