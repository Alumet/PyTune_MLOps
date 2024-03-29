from pydantic import BaseModel
from typing import Optional, List


class UserRecommendationRequest(BaseModel):
    N_track: int = 10
    filter_already_liked: bool = False


class UserSimilarRequest(BaseModel):
    track_id: int = 1
    N_track: int = 10


class AdminRecommendationRequest(BaseModel):
    user_id: int = 1
    N_track: int = 10
    filter_already_liked: bool = False


class User(BaseModel):
    user_name: str
    pass_word: str
    is_admin: bool = False


class Event(BaseModel):
    track_id: int
