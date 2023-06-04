from sqlalchemy import Column, String, Integer, DateTime

from app.db import Base


class Question(Base):
    source_id = Column(Integer)
    question = Column(String(200), index=True, unique=True)
    answer = Column(String(100))
    created = Column(DateTime)

    def __repr__(self):
        return f'Question id={self.id}'
