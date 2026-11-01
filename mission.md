# MISSION.md
# Workout Tracking API
## Main Project Mission

## 1. Project Mission

Develop a complete REST API application for tracking users' workouts and generating statistics using SQLAlchemy ORM aggregate queries and MySQL.

The application must implement all requirements from the original homework specification:

**Облік тренувань: агрегатні запити через ORM SQLAlchemy та MySQL.**

The attached `ORM_MySQL(1).docx` is the authoritative source for functional requirements, database structure, endpoint behavior, validation rules, security requirements, and bonus tasks.

The studied presentation about aggregate functions in SQLAlchemy is the technical and educational reference for implementation decisions.

The goal is to build a working, maintainable, testable application while demonstrating correct SQLAlchemy 2.1 ORM usage.

Do not omit, reinterpret, or replace mandatory requirements from the original homework.

---

## 2. Technology Stack

Use exactly the following primary technology stack:

- Python
- FastAPI
- Pydantic 2
- SQLAlchemy 2.1
- MySQL / MariaDB 10.4.32
- PyMySQL

Use modern SQLAlchemy 2.x ORM syntax.

Preferred query construction methods:

- `select()`
- `func`
- `case()`
- `distinct()`
- `session.scalar()`
- `session.execute()`
- `session.scalars()`
- `group_by()`
- `having()`
- `join()`
- `outerjoin()`
- `coalesce()`
- `nullif()`
- `subquery()`
- `scalar_subquery()`
- `over()`

Do not use deprecated SQLAlchemy query patterns.

---

## 3. Application Domain

The application manages users and their physical workouts.

A user can have multiple workouts.

Every workout belongs to one user through a foreign key.

The database must contain exactly the two required primary entities:

- `User`
- `Workout`

### User table

| Field | Type | Requirements |
|---|---|---|
| id | Integer | Primary key, autoincrement |
| name | String(100) | Required |
| email | String(255) | Unique |

### Workout table

| Field | Type | Requirements |
|---|---|---|
| id | Integer | Primary key, autoincrement |
| owner_id | Integer | Required FK to users.id |
| title | String(100) | Workout title |
| kind | String(30) | run, gym, yoga, swim |
| duration_min | Integer | Greater than zero |
| distance_km | Numeric(6,2) | Zero is allowed for gym workouts |
| done_on | Date | Workout date |

Implement the ORM relationship between `User` and `Workout`.

Respect all field types, constraints, and requirements specified in the original homework.

Do not introduce additional domain entities unless they are technically necessary and explicitly justified.

---

## 4. Project Architecture

Organize the application into clear modules.

Recommended structure:

```text
project/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── types.py
│   │
│   ├── routers/
│   │   ├── users.py
│   │   ├── workouts.py
│   │   └── stats.py
│   │
│   └── services/
│       ├── users_service.py
│       ├── workouts_service.py
│       └── stats_service.py
│
├── specs/
│
├── seed.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

This is the recommended organization. Individual implementation specifications may refine the structure while preserving separation of responsibilities.

### Architectural principles

- `models.py` contains SQLAlchemy ORM models.
- `database.py` manages the MySQL connection and database sessions.
- `schemas.py` contains Pydantic request and response schemas.
- `types.py` contains shared types and enumerations.
- `routers/` contains FastAPI endpoints.
- `services/` contains database operations and SQLAlchemy query logic.
- `seed.py` initializes the required example dataset.
- `specs/` contains independent implementation steps.

Keep route handlers simple.

Database queries and aggregate calculations belong in service functions, not directly in route handlers.

Use FastAPI dependency injection for database sessions.

Avoid unnecessary architectural complexity.

---

## 5. Database Configuration

Configure SQLAlchemy to connect to MySQL / MariaDB 10.4.32 using PyMySQL.

Use environment variables for database configuration.

Provide an `.env.example` file with the required configuration keys, without real credentials.

Configure the database connection with:

`hide_parameters=True`

Create the required tables using SQLAlchemy ORM metadata.

Ensure that database errors and API responses do not expose SQL statements, database credentials, or sensitive connection parameters.

---

## 6. Mandatory API Functionality

Implement all endpoints required by the original homework.

### Part A — Basic application functionality

#### Users

`POST /users`

Create a new user.

Validate the request using a dedicated Pydantic input schema.

Respect email uniqueness.

#### Workouts

`POST /workouts`

Create a workout associated with an existing user.

Validate the workout fields and ownership reference.

#### Workout listing

`GET /workouts`

Support:

- Filtering by `owner_id`.
- Pagination through `limit` and `offset`.
- Maximum `limit` value of 100.

Use dedicated response schemas.

### Seed data

Implement `seed.py`.

The script must create at least:

- 3 users.
- 15 workouts.
- Different workout kinds.
- Workout dates distributed across 3 months.

The dataset must make all required aggregate endpoints testable.

Use reproducible seed data.

---

## 7. Aggregate Statistics — Part B

All aggregate calculations must be performed by MySQL through SQLAlchemy ORM expressions.

Do not load all workout records into Python to calculate statistics.

### 7.1 Summary statistics

`GET /stats/summary?owner_id=1`

Return one result containing:

- Total number of workouts.
- Total workout duration in minutes.
- Total distance in kilometers.
- Average workout duration.
- Minimum distance.
- Maximum distance.

Use the appropriate aggregate functions:

- `func.count()`
- `func.sum()`
- `func.avg()`
- `func.min()`
- `func.max()`

Calculate the required values in one aggregate query.

### 7.2 Statistics by workout kind

`GET /stats/by-kind?owner_id=1`

Group workouts by `kind`.

Return:

- Workout kind.
- Workout count.
- Total duration in minutes.
- Total distance in kilometers.

Use `group_by()`.

### 7.3 Statistics by month

`GET /stats/by-month?owner_id=1`

Group workouts by calendar month.

Use the MySQL expression:

`func.date_format(Workout.done_on, "%Y-%m")`

Return:

- Month.
- Workout count.
- Total distance in kilometers.

Define the month expression once and reuse it in both `select()` and `group_by()`.

### 7.4 Top users

`GET /stats/top-users?min_workouts=3`

Return users with at least the specified number of workouts.

Use:

- `join()`
- `group_by()`
- `func.count()`
- `having()`
- Descending sorting.

The minimum workout count must be configurable through a query parameter.

### 7.5 Long workout ratio

`GET /stats/done-ratio?owner_id=1`

Calculate:

- Number of long workouts.
- Total number of workouts.

A long workout is defined as:

`duration_min >= 60`

Use conditional aggregation:

`func.count(case((Workout.duration_min >= 60, Workout.id)))`

MySQL does not support the aggregate `FILTER` syntax. Do not use it.

---

## 8. Dynamic Aggregation and Security — Part C

Implement:

`GET /stats/group?group_by=kind&metric=sum_duration&owner_id=1`

The endpoint must allow controlled selection of:

- Grouping column.
- Aggregate metric.

Use two explicit dictionaries of permitted SQLAlchemy expressions:

- `GROUP_COLUMNS`
- `METRICS`

Example:

```python
GROUP_COLUMNS = {
    "kind": Workout.kind,
}

METRICS = {
    "count": func.count(Workout.id),
    "sum_duration": func.sum(Workout.duration_min),
}
```

Retrieve SQL expressions from these dictionaries using validated request parameters.

Do not dynamically access ORM attributes or SQL functions using user-provided strings.

The following approaches are forbidden:

```python
getattr(Workout, group_by)
getattr(func, metric)
```

Use `Enum` or `Literal` for parameter validation.

Unknown grouping or metric values must produce HTTP 422.

Every statistics query must enforce the appropriate `owner_id` restriction.

---

## 9. Bonus Features

Implement bonus functionality only after all mandatory requirements are complete and verified.

### 9.1 Running cumulative distance

`GET /stats/running-total?owner_id=1`

Calculate cumulative workout distance over time.

Use a SQLAlchemy window function:

`func.sum(...).over(order_by=...)`

Return the workout date and cumulative distance.

### 9.2 Ranking workout kinds

`GET /stats/rank?owner_id=1`

Rank workout kinds according to total workout duration.

Use:

`func.rank().over(...)`

The ranking must be calculated in MySQL, not in Python.

---

## 10. Aggregate Query Implementation Rules

Follow the SQLAlchemy concepts studied in the presentation.

### 10.1 Aggregate functions

Use:

- `count`
- `sum`
- `avg`
- `min`
- `max`

Prefer calculating multiple aggregate values in one query when they describe the same result.

Use `session.scalar()` for a single scalar result.

Use `session.execute()` when selecting multiple columns.

Use `session.scalars()` when only the first selected column is needed.

### 10.2 NULL handling

Understand the difference between zero and NULL.

Important SQL behavior:

- `COUNT()` returns zero for an empty result.
- `SUM()` can return NULL when there are no matching values.
- `AVG()` can return NULL.
- `MIN()` can return NULL.
- `MAX()` can return NULL.
- Aggregate functions generally ignore NULL values within their input rows.

Where the homework requires a sum to return zero instead of NULL, use:

`func.coalesce(func.sum(...), 0)`

Use `func.nullif()` when division by zero must be avoided.

Do not automatically replace every NULL with zero. Preserve the intended meaning of each field.

### 10.3 Conditional aggregation

Use:

`func.count(case((condition, Workout.id)))`

for conditional counting.

Remember that `COUNT()` ignores NULL values.

### 10.4 GROUP BY

Every selected non-aggregated column must appear in `group_by()`.

Respect MySQL `ONLY_FULL_GROUP_BY`.

An error 1055 usually indicates that a selected non-aggregated column is missing from `GROUP BY`.

### 10.5 WHERE and HAVING

Use `where()` to filter individual database records before grouping.

Use `having()` to filter aggregated groups.

Follow this logical query structure:

1. WHERE
2. GROUP BY
3. HAVING
4. ORDER BY

### 10.6 JOIN and OUTER JOIN

Use the correct join type for the required result.

- `join()` returns matching records.
- `outerjoin()` preserves parent records without matching child records.

When counting child records after an outer join, count the child primary key rather than `count(*)`.

### 10.7 Window functions

Use `.over()` for cumulative calculations and ranking.

Do not replace database window functions with Python-side calculations.

---

## 11. Pydantic Requirements

Use Pydantic 2.

Create separate schemas for:

- User creation.
- User response.
- Workout creation.
- Workout response.
- Summary statistics.
- Statistics by kind.
- Statistics by month.
- Top users.
- Done ratio.
- Dynamic grouping.
- Bonus endpoint responses.

Input schemas must use:

`extra="forbid"`

Validate request data and query parameters.

Response schemas must reflect actual database result types, including nullable values where applicable.

Ensure that SQLAlchemy results such as `Decimal` are represented correctly in API responses.

Each endpoint must explicitly declare its response schema.

---

## 12. Error Handling and API Security

Implement consistent API error handling.

Requirements:

- Do not return SQL statements in error responses.
- Do not expose database connection strings.
- Do not expose sensitive database parameters.
- Use HTTP 404 when a requested referenced resource does not exist, where appropriate.
- Use HTTP 422 for invalid request parameters and schema validation failures.
- Enforce owner-based filtering in statistics queries.
- Validate dynamic grouping and metric parameters against the allowed values.

Never trust user-provided strings as SQL identifiers or SQL function names.

---

## 13. Testing and Verification

Test the application against the original homework requirements.

At minimum verify:

### Database
- Successful MySQL connection.
- Correct table creation.
- Primary and foreign key constraints.
- Unique email constraint.

### Basic API
- User creation.
- Workout creation.
- Workout listing.
- Owner filtering.
- Pagination.
- Invalid request handling.

### Aggregate endpoints
- Correct summary values.
- Correct grouping by kind.
- Correct grouping by month.
- Correct top-users filtering.
- Correct long-workout counting.
- Correct handling of empty sums.

### Security
- Invalid `group_by` returns 422.
- Invalid `metric` returns 422.
- Statistics respect `owner_id`.
- Error responses do not reveal SQL statements or sensitive database parameters.

### Bonus
- Correct cumulative distance.
- Correct ranking of workout kinds.

Use MySQL / MariaDB 10.4.32 for integration tests because the application depends on MySQL/MariaDB-specific behavior, including `date_format()` and grouping rules.

---

## 14. Documentation

Create a `README.md` containing:

- Project description.
- Technology stack.
- Project structure.
- Installation instructions.
- Environment configuration.
- MySQL database setup.
- Table creation.
- Seed execution.
- Application startup.
- API documentation access.
- Example requests.

Keep the detailed implementation plan in the `specs/` directory.

---

## 15. Implementation Workflow

The project must be developed incrementally.

The `specs/` directory contains individual implementation steps.

Each `spec.md` represents exactly one implementation step.

A specification must clearly define:

1. Objective.
2. Files to create.
3. Files to modify, if any.
4. Detailed implementation requirements.
5. Acceptance criteria.
6. Verification instructions.
7. Expected result.

Complete one specification before starting the next.

Do not combine multiple independent implementation steps into one uncontrolled operation.

After each step:

- Review the changed files.
- Run the relevant checks.
- Verify acceptance criteria.
- Report completed work.
- Report any unresolved issues.
- Wait for approval before proceeding to the next step.

Do not mark a step complete if its acceptance criteria have not been verified.

Do not silently skip requirements.

---

## 16. Development Principles

Follow these principles throughout implementation:

1. The attached homework DOCX is the authoritative functional specification.
2. The SQLAlchemy presentation is the technical learning reference.
3. Implement the exact required functionality before adding optional improvements.
4. Use database aggregation rather than Python-side aggregation.
5. Prefer readable SQLAlchemy expressions.
6. Keep routers, services, models, and schemas separated.
7. Respect MySQL / MariaDB 10.4.32 behavior.
8. Validate all input.
9. Protect database information.
10. Keep every implementation step independently testable.
11. Do not invent business requirements.
12. Do not introduce unnecessary functionality.

The code should be understandable to a student learning FastAPI, SQLAlchemy ORM, and aggregate SQL queries.

---

## 17. Definition of Done

The mandatory project is complete when:

- [x] Both ORM models are implemented.
- [x] MySQL connection works.
- [x] Database tables are created correctly.
- [x] All required CRUD endpoints work.
- [x] Pagination and owner filtering work.
- [x] All required Pydantic schemas are implemented.
- [x] Seed data meets the minimum requirements.
- [x] All five mandatory aggregate endpoints work.
- [x] The dynamic aggregation endpoint uses secure whitelists.
- [x] Enum or Literal validation returns HTTP 422 for invalid values.
- [x] All statistics are properly restricted by owner.
- [x] Empty aggregate results are handled correctly.
- [x] MySQL `ONLY_FULL_GROUP_BY` compatibility is verified.
- [x] SQL statements and sensitive parameters are not exposed in error responses.
- [x] README.md contains working setup instructions.
- [x] All mandatory acceptance tests pass.

Bonus endpoints are additional achievements and must not be considered prerequisites for completing the mandatory project.

---

## 18. Progress Tracker

Mark each step only after its acceptance criteria are verified.

- [x] SPEC 01 — Project foundation and database connection
- [x] SPEC 02 — ORM models and table creation
- [x] SPEC 03 — Pydantic schemas and CRUD endpoints
- [x] SPEC 04 — Seed data and basic operations check
- [x] SPEC 05 — Aggregates: summary and by-kind
- [x] SPEC 06 — Aggregates: by-month, top-users, done-ratio
- [x] SPEC 07 — Secure dynamic aggregation `/stats/group`
- [x] SPEC 08 — Window functions, final testing, documentation

---

## Final Mission

Build a complete and working Workout Tracking API that satisfies the original homework specification exactly.

Use FastAPI, Pydantic 2, SQLAlchemy 2.1 ORM, MySQL / MariaDB 10.4.32, and PyMySQL.

Demonstrate correct aggregate queries, secure dynamic grouping, proper NULL handling, and efficient database-side calculations.

Develop the application step by step according to the independent specifications in `specs/`.

The final result must be runnable, testable, understandable, and ready for demonstration.