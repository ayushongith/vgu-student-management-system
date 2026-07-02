# Student Management System

A Django-based Student Management System with role-aware dashboards, CRUD modules, REST API endpoints, reports, and JWT authentication.

## Current Modules

- Accounts and role-based access for admins, teachers, and students
- Students, teachers, departments, courses, and subjects
- Attendance, exams, marks, timetable, assignments, notices, and fees
- Reports dashboard for attendance, exams, and fees
- REST API with JWT authentication and Swagger documentation

## Local Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Set `DEBUG=True` in `.env` for local development if you want Django Debug Toolbar enabled.

## Docker Setup

```bash
copy .env.example .env
docker compose up --build
```

The application will run at `http://localhost:8000/`.

## Useful Commands

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
```

## Security Notes

- Do not use the fallback development `SECRET_KEY` in production.
- Keep `DEBUG=False` outside local development.
- Configure `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` for deployed domains.
- Set `DATABASE_NAME` when the SQLite database should live outside the project directory.
- New student and teacher accounts require explicit passwords during creation.
