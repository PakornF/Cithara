# Cithara – Django Domain Layer
**Exercise 3: Domain Layer Implementation**

---

## Project Overview

Cithara is a web-based AI song-generation system. This repository contains
the **domain layer** implemented with Django ORM, as required by Exercise 3.

---

## Quick Start

### Backend (Django)

```bash
# Create venv and install deps
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Migrate and run
python manage.py migrate
python manage.py runserver
```

Backend runs at **http://127.0.0.1:8000**

### Frontend (Next.js)

```bash
cd frontend
cp .env.local.example .env.local   # optional; defaults to http://127.0.0.1:8000
npm install
npm run dev
```

Frontend runs at **http://localhost:3000**

---

## Domain Entities Implemented

| Model | SRS Reference | Key Constraints |
|---|---|---|
| `User` | FR-01–07, C-3 | Dual auth: googleId OR passwordHash (at least one required) |
| `Song` | FR-17, FR-28–35, C-1, C-2, C-7 | Max 1M songs/user; audioFilePath only on Completed |
| `MusicGenerationRequest` | FR-08–18, FR-24–27, C-4, C-5, C-9 | Title mandatory; customStory ≤ 1000 chars; 15-min timeout |
| `ShareLink` | FR-36–41, C-6, C-8 | Composition under Song; cascade delete |
| `Feedback` | FR-50, FR-51, C-14 | Internal only; optional Song FK |

**Enumerations:** `Genre`, `Mood`, `Occasion`, `VoiceType`, `GenerationStatus`

---

## Frontend (Next.js + Tailwind)

The frontend is a responsive single-page application with:

- **Home** – Landing page and overview
- **Users** – List and create users
- **Songs** – List, create, view, delete songs; generate share links
- **Generate** – Submit music generation requests
- **Share** – View shared songs via `/share/<token>`

---

## API Endpoints

| Method | URL | Action |
|---|---|---|
| GET/POST | `/users/` | List / create users |
| GET/PATCH/DELETE | `/users/<id>/` | Get / update / delete user |
| GET/POST | `/songs/?user_id=` | List / create songs |
| GET/PATCH/DELETE | `/songs/<id>/` | Get / update / delete song |
| POST | `/songs/<id>/share/` | Create share link for song |
| GET/POST | `/requests/?user_id=` | List / create generation requests |
| GET/PATCH | `/requests/<id>/` | Get / update request |
| GET | `/share/<token>/` | Access shared song |
| GET/POST | `/feedback/` | List / submit feedback |

---

## Django Admin

```bash
python manage.py createsuperuser
```

Navigate to `http://127.0.0.1:8000/admin/` for full CRUD.

---

## Project Structure

```
cithara/
├── manage.py
├── requirements.txt
├── cithara/          # Django project
│   ├── settings.py
│   └── urls.py
├── domain/           # Domain app (models, views, admin)
└── frontend/         # Next.js + Tailwind UI
    └── src/app/      # Pages and layout
```
