# Workout Tracking API

## Опис проєкту

**Workout Tracking API** — навчальний REST API для обліку тренувань користувачів та побудови статистики. Усі підрахунки виконує СКБД (MySQL / MariaDB) через агрегатні запити SQLAlchemy 2.x ORM, а не Python.

Основні можливості:

- створення користувачів і тренувань, список тренувань із фільтром за власником та пагінацією;
- статистика: підсумок, за видами, за місяцями, топ користувачів, частка тривалих тренувань;
- безпечна динамічна агрегація через whitelist-и;
- бонус: накопичувальна дистанція (`SUM() OVER`) і рейтинг видів тренувань (`RANK() OVER`).

## Технологічний стек

- **Python** 3.11+ (перевірено на 3.14)
- **FastAPI**, **Uvicorn**
- **SQLAlchemy 2.1**, **PyMySQL**
- **Pydantic 2** (+ `email-validator`)
- **python-dotenv**
- **MySQL / MariaDB 10.4.32** (перевірено на MariaDB 10.4.32 із XAMPP)
- **pytest**, **httpx** — для тестів

## Вимоги

- Python 3.11 або новіший
- запущений сервер MySQL / MariaDB
- залежності з `requirements.txt` (для тестів — `requirements-dev.txt`)

## Структура проєкту

```text
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── users.py
│   │   ├── workouts.py
│   │   └── stats.py
│   └── services/
│       ├── users_service.py
│       ├── workouts_service.py
│       └── stats_service.py
├── specs/
├── tests/
├── seed.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── README.md
```

## Встановлення

### 1. Віртуальне середовище

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux / macOS: `python3 -m venv .venv && source .venv/bin/activate`

### 2. Залежності

```bash
pip install -r requirements.txt
```

### 3. Файл `.env`

```powershell
Copy-Item .env.example .env
```

Вкажіть свої параметри (реальний `.env` не потрапляє в Git):

```env
APP_NAME=Workout Tracking API
APP_ENV=development

DB_HOST=localhost
DB_PORT=3306
DB_USER=workout_app
DB_PASSWORD=your_password
DB_NAME=workouts_db
```

### 4. База даних

Запустіть MySQL / MariaDB і створіть базу:

```sql
CREATE DATABASE IF NOT EXISTS workouts_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Запуск

### Створення таблиць

Таблиці створюються автоматично через `Base.metadata.create_all()` під час старту застосунку (і під час запуску `seed.py`). Повторний запуск безпечний.

### Тестові дані

```bash
python seed.py
```

Створює 3 користувачів і 16 тренувань за січень–березень 2026. Повторний запуск не створює дублікатів.

### FastAPI

```bash
uvicorn app.main:app --reload
```

Swagger UI: <http://127.0.0.1:8000/docs>

### Тести

```bash
pip install -r requirements-dev.txt
pytest
```

Тести працюють із реальною БД: створюють власних користувачів з унікальними email і видаляють їх після себе. Дані `seed.py` не змінюються.

## API

Помилки валідації повертають `422`, неіснуючий власник — `404`, повторний email — `409`. У відповідях помилок немає SQL-запитів і параметрів підключення (`hide_parameters=True`). Числа типу `Decimal` у JSON серіалізуються рядками (наприклад `"37.10"`).

### CRUD

| Метод | Шлях | Опис |
|---|---|---|
| GET | `/health` | перевірка API і підключення до БД |
| POST | `/users` | створити користувача |
| POST | `/workouts` | створити тренування |
| GET | `/workouts` | список тренувань |

`POST /users`

```bash
curl -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" \
  -d '{"name": "Ivan", "email": "ivan@example.com"}'
```

```json
{"id": 1, "name": "Ivan", "email": "ivan@example.com"}
```

`POST /workouts` (`kind`: `run`, `gym`, `yoga`, `swim`; `duration_min > 0`; `distance_km >= 0`)

```bash
curl -X POST http://127.0.0.1:8000/workouts -H "Content-Type: application/json" \
  -d '{"owner_id": 1, "title": "Morning run", "kind": "run", "duration_min": 45, "distance_km": 6.50, "done_on": "2026-03-15"}'
```

```json
{"id": 1, "owner_id": 1, "title": "Morning run", "kind": "run", "duration_min": 45, "distance_km": "6.50", "done_on": "2026-03-15"}
```

`GET /workouts?owner_id=1&limit=10&offset=0` — `owner_id` необов'язковий, `limit` 1–100 (за замовчуванням 20), `offset >= 0`. Сортування за `id`. Якщо тренувань немає — `[]`.

### Основна статистика

Усі ендпоінти, окрім `top-users`, вимагають `owner_id > 0`.

| Шлях | Параметри | Опис |
|---|---|---|
| `GET /stats/summary` | `owner_id` | кількість, сума хвилин і км, середня тривалість, мін/макс дистанція |
| `GET /stats/by-kind` | `owner_id` | кількість, хвилини, км за видами |
| `GET /stats/by-month` | `owner_id` | кількість і км за календарними місяцями |
| `GET /stats/top-users` | `min_workouts` (за замовчуванням 3) | користувачі з не менш ніж N тренувань |
| `GET /stats/done-ratio` | `owner_id` | тривалі (`>= 60` хв) та всі тренування |

`GET /stats/summary?owner_id=1`

```json
{"owner_id": 1, "total_workouts": 7, "total_minutes": 425, "total_km": "37.10",
 "avg_duration": "60.7143", "min_distance": "0.00", "max_distance": "16.40"}
```

Для користувача без тренувань суми дорівнюють `0`, а `avg_duration`, `min_distance`, `max_distance` — `null`.

`GET /stats/by-kind?owner_id=1`

```json
[{"kind": "gym", "workout_count": 2, "total_minutes": 135, "total_km": "0.00"},
 {"kind": "run", "workout_count": 3, "total_minutes": 200, "total_km": "35.10"}]
```

`GET /stats/by-month?owner_id=1`

```json
[{"month": "2026-01", "workouts_count": 3, "total_distance_km": "9.50"}]
```

`GET /stats/top-users?min_workouts=5`

```json
[{"user_id": 1, "name": "Ivan Petrenko", "workouts_count": 7},
 {"user_id": 2, "name": "Olena Kovalenko", "workouts_count": 5}]
```

`GET /stats/done-ratio?owner_id=1` — для неіснуючого користувача `404`.

```json
{"owner_id": 1, "long_workouts_count": 4, "total_workouts_count": 7}
```

### Динамічна агрегація

`GET /stats/group?group_by=kind&metric=sum_duration&owner_id=1`

- `group_by`: `kind`, `owner_id`
- `metric`: `count`, `sum_duration`, `sum_distance`, `avg_duration`

```json
[{"group_value": "gym", "metric": "sum_duration", "value": 135},
 {"group_value": "run", "metric": "sum_duration", "value": 200}]
```

Параметри перевіряються через `Enum`, а вирази беруться зі словників `GROUP_COLUMNS` і `METRICS` у `stats_service.py`. Будь-яке інше значення дає `422`. `getattr` для побудови SQL не використовується.

### Бонус: window-функції

`GET /stats/running-total?owner_id=1` — накопичувальна дистанція (`SUM() OVER`, порядок `done_on, id`):

```json
[{"done_on": "2026-01-10", "distance_km": "7.50", "running_total_km": "7.50"},
 {"done_on": "2026-01-18", "distance_km": "0.00", "running_total_km": "7.50"}]
```

`GET /stats/rank?owner_id=1` — рейтинг видів за сумарною тривалістю (`RANK() OVER`, однакові суми мають однаковий ранг):

```json
[{"kind": "run", "total_duration_min": 200, "rank": 1},
 {"kind": "gym", "total_duration_min": 135, "rank": 2}]
```

## SQLAlchemy: що використано

- `func.count`, `func.sum`, `func.avg`, `func.min`, `func.max` — агрегати;
- `group_by` — групування (вираз місяця `func.date_format(done_on, "%Y-%m")` задано один раз і використано в `select`, `group_by`, `order_by`);
- `having` — фільтр груп у `top-users`;
- `case` — умовний підрахунок `func.count(case((duration_min >= 60, id)))` (MySQL не підтримує `FILTER`);
- `func.coalesce` — заміна `NULL` на `0` для сум;
- `.over()` — віконні вирази для накопичувальної суми;
- `func.rank().over(...)` — ранжування.

## Примітка про СУБД

Проєкт перевірено на MariaDB 10.4.32. Запити також сумісні з режимом `ONLY_FULL_GROUP_BY` (перевірено явним `SET SESSION sql_mode`).
