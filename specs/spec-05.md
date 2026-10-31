# SPEC 05 — Агрегатні запити: Summary та By Kind

## 1. Мета завдання

Реалізувати два статистичні GET-ендпоінти відповідно до частини B оригінального ТЗ `ORM_MySQL(1).docx`:

1. `GET /stats/summary`
2. `GET /stats/by-kind`

Основна мета — навчитися виконувати агрегатні обчислення безпосередньо в MySQL через SQLAlchemy ORM, не завантажуючи всі тренування в Python.

Використовувати знання з презентації «Агрегатні функції в SQLAlchemy»:

- `func.count()`
- `func.sum()`
- `func.avg()`
- `func.min()`
- `func.max()`
- `func.coalesce()`
- `select()`
- `where()`
- `group_by()`
- `label()`
- `session.execute()`
- `session.scalar()`

Дотримуватися `mission.md` та вже реалізованих SPEC 01–04.

## 2. Файли для створення та зміни

Очікувана структура:

```text
project/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   └── stats.py
│   │
│   └── services/
│       └── stats_service.py
│
└── ...
```

### Створити

- `app/routers/stats.py`
- `app/services/stats_service.py`

### Змінити

- `app/schemas.py`
- `app/main.py`

Якщо в проєкті вже існує статистичний роутер або сервіс, розширити наявні файли, не створюючи дублікати.

## 3. Загальні вимоги до статистичних запитів

1. Усі обчислення виконувати в MySQL.
2. Використовувати SQLAlchemy 2.1 ORM.
3. Не завантажувати всі записи `Workout` у Python для подальшого підрахунку.
4. У кожному статистичному запиті обов'язково застосовувати фільтр:

`Workout.owner_id == owner_id`

5. Якщо користувач не має тренувань, повертати коректні значення відповідно до типу агрегату.
6. Не повертати SQL-запити або параметри БД у відповідях помилок.
7. Кожен endpoint повинен мати окрему Pydantic-схему відповіді.
8. SQLAlchemy-запити реалізувати в `stats_service.py`.
9. Роутери повинні викликати функції сервісу.

## 4. Endpoint №1 — загальна статистика

### Маршрут

`GET /stats/summary?owner_id=1`

### Призначення

Отримати загальну статистику тренувань конкретного користувача одним SQL-запитом.

### Показники

| Поле відповіді | SQLAlchemy-функція | Значення |
|---|---|---|
| total_workouts | `func.count()` | Кількість тренувань |
| total_minutes | `func.sum()` | Загальна тривалість у хвилинах |
| total_km | `func.sum()` | Загальна дистанція |
| avg_duration | `func.avg()` | Середня тривалість |
| min_distance | `func.min()` | Мінімальна дистанція |
| max_distance | `func.max()` | Максимальна дистанція |

### SQLAlchemy-запит

Реалізувати функцію сервісу:

`get_summary(session, owner_id)`

Використати:

```python
stmt = (
    select(
        func.count(Workout.id).label("total_workouts"),
        func.sum(Workout.duration_min).label("total_minutes"),
        func.sum(Workout.distance_km).label("total_km"),
        func.avg(Workout.duration_min).label("avg_duration"),
        func.min(Workout.distance_km).label("min_distance"),
        func.max(Workout.distance_km).label("max_distance"),
    )
    .where(Workout.owner_id == owner_id)
)
```

Це орієнтир структури запиту. Реалізація повинна додатково забезпечити коректну обробку порожніх агрегатів і типів результатів.

Використати `session.execute(stmt).one()` або інший доречний спосіб отримання одного рядка з кількома агрегатами.

Не виконувати шість окремих запитів.

### Обробка NULL

Згідно з SQL-семантикою:

- `COUNT()` повертає 0, якщо записів немає.
- `SUM()` повертає NULL для порожнього набору.
- `AVG()` повертає NULL для порожнього набору.
- `MIN()` повертає NULL для порожнього набору.
- `MAX()` повертає NULL для порожнього набору.

Для `total_minutes` і `total_km` обов'язково замінити NULL на 0 через `func.coalesce()`.

Приклад:

```python
func.coalesce(
    func.sum(Workout.duration_min), 0
).label("total_minutes")
```

Для `avg_duration`, `min_distance` і `max_distance` зберігати семантику NULL, якщо немає тренувань.

У Pydantic-схемі ці поля повинні підтримувати nullable значення.

### Відповідь

Приклад структури:

```json
{
  "owner_id": 1,
  "total_workouts": 5,
  "total_minutes": 240,
  "total_km": 18.50,
  "avg_duration": 48.0,
  "min_distance": 0.00,
  "max_distance": 8.50
}
```

Числові значення тут ілюстративні. Фактичні результати повинні обчислюватися з даних MySQL.

## 5. Pydantic-схема SummaryResponse

Додати до `app/schemas.py`:

`SummaryResponse`

Поля:

| Поле | Тип |
|---|---|
| owner_id | int |
| total_workouts | int |
| total_minutes | int |
| total_km | Decimal або відповідний сумісний числовий тип |
| avg_duration | float або Decimal, nullable |
| min_distance | Decimal, nullable |
| max_distance | Decimal, nullable |

Вимоги:

1. Використовувати Pydantic 2.
2. Коректно обробляти `Decimal`.
3. Nullable-поля оголосити як `T | None`.
4. Не допускати помилки серіалізації числових результатів SQLAlchemy.
5. Відповідь повинна відповідати фактичним типам, які повертає MySQL.

## 6. Endpoint №2 — статистика за видом тренування

### Маршрут

`GET /stats/by-kind?owner_id=1`

### Призначення

Отримати статистику тренувань користувача з групуванням за типом тренування.

### Показники

Для кожного `kind` повернути:

- `kind` — вид тренування.
- `workout_count` — кількість тренувань.
- `total_minutes` — сумарна тривалість у хвилинах.
- `total_km` — сумарна дистанція.

### SQLAlchemy-запит

Реалізувати функцію:

`get_stats_by_kind(session, owner_id)`

Приклад структури:

```python
stmt = (
    select(
        Workout.kind,
        func.count(Workout.id).label("workout_count"),
        func.coalesce(
            func.sum(Workout.duration_min), 0
        ).label("total_minutes"),
        func.coalesce(
            func.sum(Workout.distance_km), 0
        ).label("total_km"),
    )
    .where(Workout.owner_id == owner_id)
    .group_by(Workout.kind)
    .order_by(Workout.kind)
)
```

Вимоги:

1. Групувати за `Workout.kind`.
2. Використовувати `func.count(Workout.id)`.
3. Використовувати `func.sum()` для хвилин та кілометрів.
4. Обробляти порожні суми через `coalesce()`.
5. Виконувати сортування за `kind`.
6. Використовувати `session.execute(stmt).all()`.

Усі обчислення виконуються в MySQL.

### Відповідь

Приклад структури:

```json
[
  {
    "kind": "gym",
    "workout_count": 2,
    "total_minutes": 120,
    "total_km": 0.00
  },
  {
    "kind": "run",
    "workout_count": 3,
    "total_minutes": 150,
    "total_km": 15.50
  }
]
```

Дані наведені лише для демонстрації структури. Фактичний результат залежить від seed-даних.

Якщо користувач не має тренувань, повернути порожній масив `[]`.

Не створювати штучні групи для видів тренувань, яких немає в його записах.

## 7. Pydantic-схеми By Kind

Додати до `app/schemas.py`:

### WorkoutKindStats

| Поле | Тип |
|---|---|
| kind | str або відповідний Enum |
| workout_count | int |
| total_minutes | int |
| total_km | Decimal або відповідний числовий тип |

### Загальна відповідь

Endpoint повертає список:

`list[WorkoutKindStats]`

Переконатися, що Pydantic коректно серіалізує `Decimal`.

## 8. Створення статистичного роутера

Створити `app/routers/stats.py`.

Підключити обидва endpoint-и.

### Summary

```python
@router.get(
    "/summary",
    response_model=SummaryResponse
)
```

Параметр:

`owner_id: int`

Валідація:

- Обов'язковий.
- Більший за 0.

Роутер повинен:
1. Отримати DB session через `get_db()`.
2. Викликати `get_summary()`.
3. Повернути результат відповідно до `SummaryResponse`.

### By Kind

```python
@router.get(
    "/by-kind",
    response_model=list[WorkoutKindStats]
)
```

Параметр:

`owner_id: int`

Валідація аналогічна Summary.

Роутер викликає `get_stats_by_kind()`.

## 9. Підключення роутера

Змінити `app/main.py`.

Підключити статистичний роутер через:

`app.include_router(stats.router, prefix="/stats", tags=["Statistics"])`

Зберегти працездатність:

- `GET /health`
- `POST /users`
- `POST /workouts`
- `GET /workouts`

Не змінювати поведінку вже реалізованих endpoint-ів.

## 10. Перевірка числових типів

MySQL і SQLAlchemy можуть повертати результати `Numeric` та деяких агрегатів у вигляді `Decimal`.

Обов'язково перевірити:

- `total_km`
- `min_distance`
- `max_distance`
- `avg_duration`
- `total_km` у групуванні за видом.

Не перетворювати `Decimal` на `float` без потреби.

Не допускати втрати точності дистанції.

Переконатися, що API повертає коректний JSON.

## 11. Критерії приймання

### Summary

- [ ] Реалізовано `GET /stats/summary`.
- [ ] Є обов'язковий `owner_id`.
- [ ] Працює фільтр за власником.
- [ ] Кількість тренувань обчислюється через `count`.
- [ ] Сума хвилин обчислюється через `sum`.
- [ ] Сума кілометрів обчислюється через `sum`.
- [ ] Середня тривалість обчислюється через `avg`.
- [ ] Мінімальна дистанція обчислюється через `min`.
- [ ] Максимальна дистанція обчислюється через `max`.
- [ ] Для порожніх сум використовується `coalesce`.
- [ ] Nullable-поля правильно обробляються.
- [ ] Усі показники отримуються одним SQL-запитом.
- [ ] Реалізовано `SummaryResponse`.

### By Kind

- [ ] Реалізовано `GET /stats/by-kind`.
- [ ] Працює фільтр за власником.
- [ ] Використовується `group_by(Workout.kind)`.
- [ ] Рахується кількість тренувань.
- [ ] Рахується сума хвилин.
- [ ] Рахується сума кілометрів.
- [ ] Порожній результат повертає `[]`.
- [ ] Результати стабільно відсортовані.
- [ ] Реалізовано `WorkoutKindStats`.

### Загальні вимоги

- [ ] SQLAlchemy-запити розташовані в сервісі.
- [ ] Роутер не містить агрегатної SQL-логіки.
- [ ] Використовується MySQL / MariaDB 10.4.32.
- [ ] Працює Pydantic 2.
- [ ] Числові типи коректно серіалізуються.
- [ ] Усі попередні endpoint-и продовжують працювати.

## 12. Перевірка роботи

Виконати перевірку через Swagger UI або HTTP-клієнт.

### 12.1 Summary

Запит:

`GET /stats/summary?owner_id=1`

Перевірити:
1. Правильну кількість тренувань.
2. Правильну суму хвилин.
3. Правильну суму кілометрів.
4. Середню тривалість.
5. Мінімальну та максимальну дистанцію.
6. Відсутність тренувань у користувача.
7. Коректні значення `0` та `null` у порожньому результаті.

Додатково перевірити, що тренування іншого користувача не потрапляють у результат.

### 12.2 By Kind

Запит:

`GET /stats/by-kind?owner_id=1`

Перевірити:
1. Наявність лише видів тренувань, які має користувач.
2. Правильний підрахунок кожного виду.
3. Правильну суму хвилин.
4. Правильну суму кілометрів.
5. Коректне сортування.
6. Порожній масив для користувача без тренувань.

### 12.3 Додаткові перевірки

- Передати `owner_id=0`.
- Передати від'ємний `owner_id`.
- Перевірити HTTP 422.
- Переконатися, що SQL-запити не виконуються в Python через завантаження всіх тренувань.
- Перевірити відповідність результатів контрольним SQLAlchemy-обчисленням на seed-даних.

## 13. Межі завдання

У цьому SPEC НЕ реалізовувати:

- `/stats/by-month`
- `/stats/top-users`
- `/stats/done-ratio`
- `/stats/group`
- `/stats/running-total`
- `/stats/rank`

Це буде реалізовано в наступних SPEC.

## 14. Звіт про завершення

Після реалізації надати звіт:

1. Створені та змінені файли.
2. Реалізація `get_summary()`.
3. Реалізація `get_stats_by_kind()`.
4. Створені Pydantic-схеми.
5. Результати перевірки обох endpoint-ів.
6. Результати перевірки `NULL` та `coalesce`.
7. Результати перевірки фільтрації за `owner_id`.
8. Перевірка типів `Decimal`.
9. Виявлені проблеми.

Не позначати SPEC 05 завершеним без перевірки обох endpoint-ів на реальній MySQL / MariaDB 10.4.32.

Після завершення зупинитися та чекати підтвердження перед переходом до SPEC 06.