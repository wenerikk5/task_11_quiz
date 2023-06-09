# quiz

## Описание задания

API-сервис для добавления вопросов для викторины в локальную базу данных из публичного API (https://jservice.io/api/random?count=1). Данные сохраняются в базе со следующими полями:
- id - первичный ключ вопроса в локальной базе данных;
- source_id - id вопроса (из ответа публичного API);
- question - текст вопроса (длина вопроса не более 200 символов);
- answer - текст ответа на вопрос (длина не более 100 символов);
- created - дата создания вопроса (из ответа публичного API, поле created_at).
Сохраняются только уникальные вопросы.

POST-запрос на добавление вопросов должен содержать количество вопросов для добавления в виде: {"questions_num": integer}

В ответе на POST-запрос будет получен последний сохраненный вопрос для викторины, либо пустой объект (если записей в базе данных еще нет).


##  Использованный стек

- Python 3 - аннотации типов потребуют версии 3.10+
- FastAPI - фреймворк
- PostgreSQL - база данных
- SQLAlchemy - ORM
- Alembic - миграции для ORM
- uvicorn - ASGI веб-сервер
- Docker - проект разворачивается с помощью docker-compose

##  Установка

Команды в терминале должны выполняться из основной директории проекта (директория с файлом docker-compose.yml). 

```
# Переименовать файл .env-example в .env командой:
mv .env-example .env

# Сборка образов и запуск в контейнерах:
docker-compose up -d --build

# Проверка запущенных контейнеров (должно быть 2 сервиса: web и db)
docker ps
```

После запуска контейнеров будет автоматически выполнена инициализация базы данных (применена сохраненная миграция alembic).

## Использование

При использовании Postman направить POST-запрос:
- URL: http://127.0.0.1/add-questions
- Тело запроса в формате JSON: {"questions_num":  integer}

Количество вопросов должно быть целым числом от 1 до 500. При отстуствии тела запроса или некорректной записи будет использовано дефолтное значение - {"questions_num":  1}.

Также запросы можно направить из браузера через Swagger (http://127.0.0.1/docs).


## Детали реализации и ограничения

Один запрос к публичному API позволяет получить не более 100 вопросов. Для возможности получения большего числа вопросов приложение асинхронно направляет несколько запросов, после чего проверяет наличие каждого полученного вопроса в БД и формирует список новых уникальных вопросов для сохранения. 

В случае, если часть вопросов не проходит валидацию на уникальность, выполняются повторые запросы (итерации) до достижения необходимого количества вопросов. Во избежание продолжительной обработки запроса, в приложении ограничено количество итераций - не более 5 циклов повторных запросов к внешнему API. При достижении лимита итераций в БД будет сохранено сформированное количество уникальных вопросов. 

Например, мы запросили 500 вопросов, приложение в первой итерации направит к публичному API 5 запросов по 100 вопросов в каждом. Если после валидации, окажется, что получено только 300 уникальных вопросов, будет выполнена вторая итерация - направлено 2 запроса по 100 вопросов в каждом. И т.д. до достижения либо необходимого количества уникальных вопросов (500 вопросов) либо лимита на количество итераций (5 итераций).
