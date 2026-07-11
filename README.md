# AI Resume Analyzer

A Django web app that uploads PDF, DOC, or DOCX resumes and shows an ATS-style analysis dashboard.

## Features

- Resume upload flow for PDF, DOC, and DOCX files
- PDF text extraction with `pypdf`
- DOCX text extraction using standard Python libraries
- Skill detection
- Contact detail checks
- Important section checks
- Resume score and improvement suggestions
- Django admin support
- Automated tests

## Tech Stack

- Python
- Django
- SQLite
- HTML/CSS
- pypdf

## Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Notes

Uploaded resumes, local database files, and virtual environments are intentionally ignored by git.


## Deployment

This project is ready for a Render web service. The included `render.yaml` sets the build command, start command, and required environment variables.

Required production settings:

```text
DJANGO_SECRET_KEY=<generated secret>
DEBUG=False
ALLOWED_HOSTS=.onrender.com
CSRF_TRUSTED_ORIGINS=https://*.onrender.com
```

Uploaded files are stored in `media/`. On free hosting, uploaded files may be temporary unless persistent storage is configured.
