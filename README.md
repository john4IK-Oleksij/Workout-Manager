# Workout Tracking API

## Призначення проєкту

**Workout Tracking API** — це REST API застосунок для обліку тренувань користувачів та побудови аналітичної статистики за допомогою SQLAlchemy 2.x ORM та СКБД MySQL / MariaDB 10.4.32.

## Технологічний стек

- **Python** 3.11+
- **FastAPI** — вебфреймворк для побудови REST API
- **Uvicorn** — ASGI-сервер для запуску застосунку
- **SQLAlchemy 2.x (2.1)** — ORM для роботи з базою даних
- **PyMySQL** — драйвер підключення до MySQL / MariaDB
- **Pydantic 2** — валідація та серіалізація даних
- **python-dotenv** — завантаження конфігурації зі змінних середовища (`.env`)
- **MySQL / MariaDB 10.4.32** — реляційна система керування базами даних

## Початкова структура проєкту

```text
project/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── database.py
│
├── specs/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Встановлення та налаштування

### 1. Створення та активація віртуального середовища

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 3. Конфігурація змінних середовища (`.env`)

Створіть локальний файл `.env` на основі шаблону `.env.example`:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Відредагуйте файл `.env`, вказавши реальні параметри підключення до вашого сервера MySQL / MariaDB 10.4.32:

```env
APP_NAME=Workout Tracking API
APP_ENV=development

DB_HOST=localhost
DB_PORT=3306
DB_USER=workout_app
DB_PASSWORD=your_password
DB_NAME=workouts_db
```

### 4. Підготовка та запуск MySQL / MariaDB 10.4.32

1. Переконайтеся, що сервер **MySQL / MariaDB 10.4.32** встановлений та запущений (на стандартному порту `3306` або іншому, вказаному в `.env`).
2. Створіть базу даних `workouts_db` (якщо вона ще не створена):

```sql
CREATE DATABASE IF NOT EXISTS workouts_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Запуск застосунку

Запустіть сервер розробки за допомогою Uvicorn:

```bash
uvicorn app.main:app --reload
```

Після запуску сервер буде доступний за адресою: `http://127.0.0.1:8000`

Інтерактивна документація Swagger UI доступна за адресою:
- `http://127.0.0.1:8000/docs`

## Перевірка працездатності (`GET /health`)

Виконайте запит до тестового ендпоінта:

```bash
curl http://127.0.0.1:8000/health
```

Або відкрийте у браузері: `http://127.0.0.1:8000/health`

Очікувана відповідь (`HTTP 200 OK`):

```json
{
  "status": "ok",
  "application": "Workout Tracking API"
}
```

