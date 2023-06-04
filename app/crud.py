from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Question
from app.schemas import QuestionCreate
from app.db import AsyncSessionLocal


async def get_question_from_db(
        question: str,
        db_session: AsyncSession,
) -> Question | None:
    db_question = await db_session.execute(
        select(Question).where(
            Question.question == question
        )
    )
    return db_question.scalars().first()


async def add_multiple_questions_in_db(
        new_questions: list[QuestionCreate],
        db_session: AsyncSession,
) -> None:
    for new_question in new_questions:
        new_question = Question(**new_question)
        db_session.add(new_question)

    await db_session.commit()


async def check_question_exist_in_db(
        question: str,
        db_session: AsyncSession,
) -> bool:
    db_question = await get_question_from_db(question, db_session)

    if db_question:
        return True
    return False


async def get_last_question_from_db(
        db_session: AsyncSession
) -> Question | dict:
    async with AsyncSessionLocal() as db_session:
        db_question = await db_session.execute(
            select(Question).order_by(Question.id.desc())
        )
        db_question = db_question.scalars().first()

    if not db_question:
        return {}
    return db_question
