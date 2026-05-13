<p align="center" style="padding-top: 30px;">
  <img src="https://raw.githubusercontent.com/TopNik073/obuv-demo-ex/main/static/logo.svg" alt="Обувь — склад" width="280"><br>
  <span style="font-size: 18px;">Демо учёт товаров и заказов для ООО «Обувь»</span>
</p>

## О проекте

Настольное веб-приложение (окно на **pywebview** + **FastAPI**): вход по логину, роли **гость**, **клиент**, **менеджер**, **администратор**, справочник товаров с остатками и скидками, заказы с привязкой к клиенту, админка пользователей. Данные в **SQLite** (файл рядом с приложением), схема через **Alembic**.

## Стек

Python 3.13, FastAPI, SQLAlchemy 2 (async), Pydantic, Alembic, aiosqlite, JWT, pywebview, uvicorn.

## Быстрый старт

1. Установить зависимости: `uv sync --group dev` (из корня репозитория; в группе `dev` — ruff и def-form для линтеров).
2. Создать `.env` в корне (рядом с `pyproject.toml`) с секретами и путём к базе, например: `SQLITE_DATABASE_PATH` (по умолчанию `obuv.sqlite` в корне проекта), `JWT_SECRET`, при необходимости `ADMIN_BOOTSTRAP_PASSWORD` для первого администратора. При необходимости можно задать полный URL `DATABASE_URL` вместо `SQLITE_DATABASE_PATH`.
3. Применить миграции: `uv run alembic upgrade head`.
4. Запуск API из каталога `src`: `cd src && uv run uvicorn main_app:app --host 127.0.0.1 --port 8000` (порт можно переопределить в `.env`).
5. Запуск окна приложения: `cd src && uv run python desktop.py` (поднимает тот же API в фоне и открывает интерфейс).

Импорт демо-товаров: в интерфейсе администратора раздел «Товары» — импорт CSV из `resources/import/demo_products.csv`.

## Сборка Windows (.exe)

Локально (из корня репозитория, нужен установленный [uv](https://docs.astral.sh/uv/)):

1. `uv sync --group dev` — в группе `dev` лежит PyInstaller.
2. `uv run pyinstaller desktop.spec` — результат: `dist/obuv-demo-ex.exe` (onefile).

Рядом с exe положите `.env` с теми же переменными, что и при разработке (приложение читает конфиг из каталога с исполняемым файлом). Файл SQLite по умолчанию создаётся рядом с exe (или по пути из `SQLITE_DATABASE_PATH`). При старте exe выполняется `alembic upgrade head` до открытия окна.

**Релиз на GitHub:** при пуше тега вида `v*.*.*` (например `v0.1.0`) workflow [`.github/workflows/desktop-exe.yml`](.github/workflows/desktop-exe.yml) собирает exe и публикует [GitHub Release](https://docs.github.com/en/repositories/releasing-projects-on-github) с этим файлом в качестве вложения.
