<p align="center" style="padding-top: 30px;">
  <img src="https://raw.githubusercontent.com/TopNik073/obuv-demo-ex/main/static/logo.svg" alt="Обувь — склад" width="280"><br>
  <span style="font-size: 18px;">Демо учёт товаров и заказов для ООО «Обувь»</span>
</p>

## О проекте

Настольное веб-приложение (окно на **pywebview** + **FastAPI**): вход по логину, роли **гость**, **клиент**, **менеджер**, **администратор**, справочник товаров с остатками и скидками, заказы с привязкой к клиенту, админка пользователей. Данные в **PostgreSQL**, схема через **Alembic**.

## Стек

Python 3.13, FastAPI, SQLAlchemy 2 (async), Pydantic, Alembic, asyncpg, JWT, pywebview, uvicorn.

## Быстрый старт

1. Установить зависимости: `uv sync` (из корня репозитория).
2. Создать `.env` в корне (рядом с `pyproject.toml`) с переменными подключения к БД и секретами, например: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_NAME`, `JWT_SECRET`, при необходимости `ADMIN_BOOTSTRAP_PASSWORD` для первого администратора.
3. Применить миграции: `uv run alembic upgrade head`.
4. Запуск API из каталога `src`: `cd src && uv run uvicorn main_app:app --host 127.0.0.1 --port 8000` (порт можно переопределить в `.env`).
5. Запуск окна приложения: `cd src && uv run python desktop.py` (поднимает тот же API в фоне и открывает интерфейс).

Импорт демо-товаров: в интерфейсе администратора раздел «Товары» — импорт CSV из `resources/import/demo_products.csv`.

## Лицензия и артефакты экзамена

Учебный демонстрационный проект. Отчётные PDF/DOCX по заданию в репозиторий не включались.

После публикации на GitHub при желании замените в атрибуте `src` у тега `img` путь на абсолютный URL, например `https://raw.githubusercontent.com/USER/REPO/main/static/logo.svg` (подставьте `USER` и `REPO`), чтобы логотип отображался там, где README открывают без клонирования репозитория.
