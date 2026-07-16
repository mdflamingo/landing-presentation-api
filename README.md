# Landing Presentation API

Backend-сервис для лендинг-презентации разработчика с AI-интеграцией.

## Архитектура

```
app/
├── main.py                # FastAPI приложение, CORS, глобальные обработчики
├── config.py              # Настройки из .env
├── db.py                  # SQLAlchemy async engine + сессии
├── logging_config.py      # Конфигурация логирования
├── models/
│   ├── contact.py         # Pydantic модели (вход/выход)
│   └── db_models.py       # SQLAlchemy ORM модели
├── routers/               # API эндпоинты (контроллеры)
│   ├── contact.py         # POST /api/contact
│   ├── health.py          # GET /api/health
│   └── metrics.py         # GET /api/metrics
├── services/              # Бизнес-логика
│   ├── contact_service.py
│   ├── email_service.py
│   └── ai_service.py      # OpenAI интеграция + fallback
├── storage/
│   └── repositories.py    # Репозитории (SQLAlchemy async)
└── middleware/
    └── logging_middleware.py

alembic/                   # Миграции БД
├── env.py
└── versions/
    └── 001_initial_schema.py
```

## Быстрый старт

```bash
# Установка uv (если нет)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка зависимостей
uv sync

# Настройка окружения
cp .env.example .env
# отредактируйте .env (DATABASE_URL, OPENAI_API_KEY)

# Миграции БД
uv run alembic upgrade head

# Запуск
uv run uvicorn app.main:app --reload
# или
make dev
```

## PostgreSQL

```bash
# Создание БД
createdb landing_api

# Миграции
uv run alembic upgrade head

# Новая миграция
uv run alembic revision --autogenerate -m "описание"
uv run alembic upgrade head
```

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/contact` | Форма обратной связи |
| `GET` | `/api/health` | Статус сервиса |
| `GET` | `/api/metrics` | Статистика обращений |
| `GET` | `/api/docs` | Swagger UI |
| `GET` | `/api/redoc` | ReDoc |

## AI-интеграция

`app/services/ai_service.py` — анализирует каждое обращение через OpenAI:
- **Тональность**: позитивная / негативная / нейтральная
- **Категория**: вопрос / заказ / жалоба / предложение / сотрудничество / другое
- **Рекомендуемый ответ**: генерируется AI

Graceful fallback: если OpenAI недоступен, используется keyword-based анализ.

## Rate Limiting

Защита от спама через PostgreSQL (по IP). Настройки в `.env`:
- `RATE_LIMIT_MAX_REQUESTS` — максимум запросов (по умолчанию 10)
- `RATE_LIMIT_WINDOW_SECONDS` — окно в секундах (по умолчанию 60)

## Команды

```bash
make install   # uv sync
make dev       # запуск с --reload
make run       # продакшн запуск
make migrate   # alembic upgrade head
make lint      # ruff check + mypy
```
