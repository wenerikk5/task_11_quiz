from pydantic import BaseModel
from datetime import datetime


class QuestionCreate(BaseModel):
    source_id: int | None
    question: str
    answer: str
    created: datetime


class QuestionDB(QuestionCreate):
    id: int

    class Config:
        orm_mode = True
