# Tutor Booking

Учебный full-stack проект: запись клиентов на занятия.

## Что выполнено

- 60 use cases, из них 20 отмечены как MVP;
- роли `client` и `admin`;
- JWT-авторизация;
- 2 бизнес-сущности с CRUD: `Subject` и `Booking`;
- Backend: FastAPI + SQLAlchemy;
- Database: PostgreSQL;
- UI: React + Vite + Nginx;
- всё запускается через Docker Compose.

## Быстрый запуск

1. Установить Docker Desktop.
2. Открыть терминал в корне проекта.
3. Выполнить:

```bash
docker compose up --build
```

4. Открыть:
   - UI: http://localhost:3000
   - Swagger API: http://localhost:8000/docs

### Тестовый администратор

- Email: `admin@example.com`
- Password: `admin12345`

Обычного клиента можно зарегистрировать через интерфейс.

## Остановка

```bash
docker compose down
```

Удалить контейнеры вместе с данными PostgreSQL:

```bash
docker compose down -v
```

## Структура

```text
tutor-booking/
├── backend/              # FastAPI сервер
│   ├── app/
│   │   ├── routers/      # REST endpoints
│   │   ├── auth.py       # JWT и роли
│   │   ├── database.py   # подключение к PostgreSQL
│   │   ├── models.py     # модели БД
│   │   ├── schemas.py    # схемы API
│   │   └── main.py       # запуск приложения
│   └── Dockerfile
├── frontend/             # React UI
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── docs/
│   ├── use-cases.md
│   └── project-description.md
├── docker-compose.yml
└── README.md
```

## CRUD API

### Subjects

- `GET /subjects`
- `GET /subjects/{id}`
- `POST /subjects` — admin
- `PUT /subjects/{id}` — admin
- `DELETE /subjects/{id}` — admin

### Bookings

- `GET /bookings`
- `GET /bookings/{id}`
- `POST /bookings`
- `PUT /bookings/{id}`
- `DELETE /bookings/{id}`

## Git / GitHub

После создания пустого репозитория на GitHub:

```bash
git init
git add .
git commit -m "Initial MVP"
git branch -M main
git remote add origin https://github.com/USERNAME/tutor-booking.git
git push -u origin main
```

Заменить `USERNAME` на свой логин GitHub.
