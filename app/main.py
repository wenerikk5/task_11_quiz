import aiohttp
import asyncio
import time
import datetime
from fastapi import FastAPI, Depends, Query, HTTPException, Request, Body

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session, AsyncSessionLocal
from app.config import config
from app.schemas import QuestionCreate, QuestionDB

from app.crud import (get_last_question_from_db, check_question_exist_in_db,
                      add_multiple_questions_in_db)


app = FastAPI(title=config.APP_TITLE)

source_url = 'https://jservice.io/api/random?count='


@app.post(
        '/add-questions',
        response_model=QuestionDB | dict
)
async def add_questions_in_db(
    request: dict[str, int] = Body({'questions_num': 1}),
    db_session: AsyncSession = Depends(get_async_session),
):
    start = time.perf_counter()

    questions_num = request.get('questions_num', 1)

    if questions_num < 1 or questions_num > 500:
        raise HTTPException(
                status_code=422,
                detail='Значение количества вопросов должно быть '
                'целым числом в интервале от 1 до 500.'
            )

    last_question = await get_last_question_from_db(db_session)
    results = await get_questions_proceed(questions_num)
    await add_multiple_questions_in_db(results, db_session)

    print(f'Продолжительность обработки: {time.perf_counter() - start} с.')
    return last_question


async def get_questions_request(
        num: int,
):
    error = False
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{source_url}{num}') as response:
            # In case of overloading server do not reply with json
            try:
                results = await response.json()
            except:
                error = True

    outcomes: list[QuestionCreate] = []

    async with AsyncSessionLocal() as db_session:
        for result in results:
            try:
                # validate question's uniqness in db and lengths:
                if (
                    result
                    and 1 < len(result.get('question')) < 200
                    and 1 < len(result.get('answer')) < 100
                    and not await check_question_exist_in_db(
                        result.get('question'),
                        db_session
                    )
                ):
                    outcomes.append({
                        'source_id': result.get('id'),
                        'question': result.get('question'),
                        'answer': result.get('answer'),
                        'created': (datetime.datetime.fromisoformat(
                            result.get('created_at')).replace(tzinfo=None))
                    })
            except:
                error = True
                break
    # return an empty list to increase iteratons_counter
    if error:
        return []
    return outcomes


async def get_questions_task(
        questions_num: int,
) -> list[QuestionCreate]:
    tasks = []

    # create tasks with limit 100 questions per request
    for i in range(1, (questions_num - 1) // 100 + 2):
        if i != (questions_num - 1) // 100 + 1:
            tasks.append(asyncio.create_task(
                get_questions_request(100))
            )
        else:
            tasks.append(asyncio.create_task(
                get_questions_request(questions_num - 100 * (i - 1))
            ))
    results = await asyncio.gather(*tasks)

    outcomes: list[QuestionCreate] = []
    # join all results in one list
    for result in results:
        outcomes += result
    return outcomes


async def get_questions_proceed(
        questions_num: int,
) -> list[QuestionCreate]:
    data: list[QuestionCreate] = []     # collect results
    i: int = 0                          # unique questions counter
    loop_count: int = 0                 # iterations counter
    loop_limit: int = 5                 # limit for iteraions

    while i < questions_num and loop_count < loop_limit:
        results = await get_questions_task(questions_num - i)
        if results:
            for item in results:
                # collect unique questions in data
                if item not in data:
                    data.append(item)
                    i += 1
        loop_count += 1

    # if for several iterations we hit loop_limit and have no new questions
    # external API might be overloaded or there is no much unique questions
    if loop_count == loop_limit and i == 0:
        raise HTTPException(
                status_code=503,
                detail='Добавление вопросов в базу временно недоступно.'
            )
    elif loop_count == loop_limit and i < questions_num:
        print(f'Количество итераций достигло лимита ({loop_limit} попыток),'
              f'в базу добавлено только {i} новых вопросов.')
    return data
