# Cithara – Django Domain Layer
**Exercise 3: Domain Layer Implementation**

---

## Project Overview

Cithara is a web-based AI song-generation system. This repository contains
the **domain layer** implemented with Django ORM, as required by Exercise 3.

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

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip

### 1. Clone and enter the project
```bash
git clone <your-repo-url>
cd cithara
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (for Django Admin)
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

The server starts at `http://127.0.0.1:8000/`

---

## CRUD Operations

### Via Django Admin
Navigate to `http://127.0.0.1:8000/admin/` and log in with your superuser credentials.

All five domain entities are registered with full CRUD support:
- `domain | User` – create, list, edit, delete
- `domain | Song` – inline ShareLink, Feedback, and GenerationRequests
- `domain | Music Generation Request` – shows timed-out flag
- `domain | Share Link`
- `domain | Feedback`

### Via JSON API Endpoints

#### Users
| Method | URL | Action |
|---|---|---|
| GET | `/users/` | List all users |
| POST | `/users/` | Create user |
| GET | `/users/<id>/` | Get user |
| PATCH | `/users/<id>/` | Update user |
| DELETE | `/users/<id>/` | Delete user |

**Create user (POST /users/)**
```json
{
  "email": "alice@example.com",
  "name": "Alice",
  "google_id": "google-uid-123"
}
```

#### Songs
| Method | URL | Action |
|---|---|---|
| GET | `/songs/?user_id=1` | List songs for a user |
| POST | `/songs/` | Save a song |
| GET | `/songs/<id>/` | Get song + share link |
| PATCH | `/songs/<id>/` | Update song |
| DELETE | `/songs/<id>/` | Permanently delete (C-12) |

**Create song (POST /songs/)**
```json
{
  "owner_id": 1,
  "title": "Happy Birthday Song",
  "genre": "Pop",
  "mood": "Happy",
  "occasion": "Birthday",
  "voice_type": "Female",
  "status": "Completed",
  "audio_file_path": "/audio/happy-birthday.mp3"
}
```

#### Generation Requests
| Method | URL | Action |
|---|---|---|
| GET | `/requests/?user_id=1` | List requests |
| POST | `/requests/` | Submit new request |
| GET | `/requests/<id>/` | Get request + timeout check |
| PATCH | `/requests/<id>/` | Update status |

**Submit request (POST /requests/)**
```json
{
  "user_id": 1,
  "title": "Wedding Waltz",
  "genre": "Classical",
  "mood": "Romantic",
  "occasion": "Wedding",
  "voice_type": "Female",
  "custom_story": "A song for our first dance."
}
```

#### Shared Song
| Method | URL | Action |
|---|---|---|
| GET | `/share/<token>/` | Access shared song (UC-10) |

#### Feedback
| Method | URL | Action |
|---|---|---|
| GET | `/feedback/` | List feedback (internal) |
| POST | `/feedback/` | Submit feedback |

---

## Design Decisions and Deviations

| Decision | Justification |
|---|---|
| Dual auth via optional `google_id` / `password_hash` | FR-01, FR-02; constraint C-3 enforced in `User.clean()` |
| JWT not stored on User | FR-04, FR-06: JWT is stateless per-request; storing it would contradict its design |
| `audioFilePath` optional on Song | C-7: only populated when `GenerationStatus = Completed` |
| `expiresAt` on ShareLink present but null | Open Issue 5: retained to avoid future schema change |
| Feedback → Song FK optional | FR-50: feedback may be general; modelling assumption documented in Exercise 2 |
| `MusicGenerationRequest` preserved on failure | Assumption 6, FR-24: enables retry without re-entering inputs |
| `GenerationStatus` as TextChoices enum | Business rule, not user data; no join complexity needed |
| Max 1,000,000 songs enforced in `Song.save()` | NFR-26, C-2 |

---

## Project Structure

```
cithara/
├── manage.py
├── requirements.txt
├── README.md
├── cithara/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── domain/
    ├── __init__.py
    ├── apps.py
    ├── models.py       ← Domain entities (core deliverable)
    ├── admin.py        ← CRUD via Django Admin
    ├── views.py        ← CRUD via JSON API
    ├── urls.py
    └── migrations/
        ├── __init__.py
        └── 0001_initial.py
```

---

## Traceability

The implementation is consistent with the domain model in Exercise 2.
All constraints (C-1 through C-14), functional requirements (FR-01 through FR-51),
and user stories are mapped in the inline comments of `models.py`.
