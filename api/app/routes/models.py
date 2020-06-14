from pydantic import BaseModel
from enum import Enum
from typing import List, Tuple


class PredictionType(Enum):
    straight = 'straight'
    gay = 'gay'


class DetectedFace(BaseModel):
    prediction: PredictionType
    accuracy: float
    cords: Tuple[int, int, int, int]


class DetectionResponse(BaseModel):
    count: int
    faces: List[DetectedFace]
