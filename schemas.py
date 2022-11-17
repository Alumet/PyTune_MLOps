from pydantic import BaseModel
from typing import Optional, List


class RecommendationRequest(BaseModel):
    user_id: int = 1
    N_track: int = 10
    filter_already_liked: bool = False


class RecommendationResult(BaseModel):
    track_id: int
    score: float
    track_name: str
    artist_name: str
