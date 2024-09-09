# FastAPI Boilerplate

Scalable starting point for building web applications using the FastAPI framework. It provides a structured project setup with essential features and best practices, allowing developers to quickly kickstart their project.

## Prerequisite

### Setup Configuration

- Copy `.example.env` file to `.env` on the root folder
- Fill config value directly there

### How do I run locally?

- Setup Configuration in above section
- Install the dependencies: `pip install -r requirements.txt`
- Run API: `uvicorn main:app --host 127.0.0.1 --port 8080 --reload`

### Database Migrations

- Library: <https://alembic.sqlalchemy.org/>
- Getting started:
  - create new postgresql database, e.g. appdb
  - setup database configuration in `.env` file
  - `alembic upgrade head`
  - add new model and ensure it is properly imported to the `table.py`
  - `alembic revision --autogenerate -m "migration name"`

### Who do I talk to?

- Repo owner or admin
