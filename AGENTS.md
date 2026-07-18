# GameSite Contributor Guide

## Project overview

This repository is a Django project. `Config` contains the project configuration and URL routing; `Backend` is the application that provides models, serializers, validators, permissions, view sets, and routes.

## Working conventions

- Keep changes focused on the requested feature or fix.
- Follow existing Django and Django REST Framework patterns in the relevant module.
- Place schema changes in `Backend/migrations` using Django-generated migrations; do not edit applied migrations.
- Keep model, serializer, validator, permission, view-set, and URL changes consistent when adding or changing an API capability.
- Do not commit local artifacts such as `.venv`, `__pycache__`, SQLite database changes, or IDE workspace files unless explicitly requested.
- Preserve the existing directory names, including legacy spellings such as `tamplates`, `registation_views`, `coments_validators`, and `game_rations_serializers`, unless a task explicitly includes a coordinated rename.

## Validation

Run the relevant checks from the repository root when dependencies are available:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

For model changes, also create and review migrations:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

## Configuration and data safety

- Treat `Config/settings.py` as environment-sensitive: do not expose secrets or weaken production security settings.
- Avoid destructive database commands or data migrations unless the task explicitly requires them.
