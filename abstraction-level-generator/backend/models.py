# backend/models.py

from pydantic import BaseModel
from typing import List, Dict, Optional

class Question(BaseModel):
    raw_question: str

class AbstractionLevel(BaseModel):
    level_number: int
    ideal_representation: str
    generated_question: str
    score: float
    variables: Dict[str, str]

class AbstractionResponse(BaseModel):
    question_id: int
    levels: List[AbstractionLevel]

class APIResponse(BaseModel):
    choices: List[Dict[str, str]]

