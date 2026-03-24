# Cithara 🎵

> AI-powered song generation — create, manage, and share personalised music in seconds.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 5, SQLite (dev) |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **AI Generation** | Suno AI (async background thread) |
| **Auth** | Email + verification code · Google OAuth (JWT) |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # fill in your values
python manage.py migrate
python manage.py runserver 8001
```

Backend runs at **http://127.0.0.1:8001**

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local      # fill in your values
npm run dev
```

Frontend runs at **http://localhost:3000**

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `EMAIL_HOST` | SMTP host (e.g. `smtp.gmail.com`) |
| `EMAIL_PORT` | SMTP port (e.g. `587`) |
| `EMAIL_USE_TLS` | Use TLS (`true` / `false`) |
| `EMAIL_HOST_USER` | Sender email address |
| `EMAIL_HOST_PASSWORD` | App password (Gmail: enable 2FA → [App Password](https://myaccount.google.com/apppasswords)) |
| `DEFAULT_FROM_EMAIL` | From header for verification emails |
| `SUNO_AI_API_KEY` | Suno API key |
| `SUNO_API_BASE_URL` | Suno API base URL (default: `https://api.sunoapi.org`) |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Django backend base URL (default: `http://127.0.0.1:8001`) |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Google OAuth client ID for web login |

> **Dev tip:** If email is not configured, verification codes are printed to the Django terminal instead.

---

## Pages

| Route | Description |
|---|---|
| `/` | Landing page & login / sign-up |
| `/dashboard` | Personalised hub with quick links |
| `/songs` | Your saved song library — play, share, delete |
| `/songs/[id]` | Song detail with audio player |
| `/requests` | Submit a new AI generation request |
| `/users` | Browse all creators |
| `/users/[id]/songs` | View another user's song library |
| `/share/[token]` | Public shared song page (no login required) |

---

## API Endpoints

### Auth
| Method | URL | Action |
|---|---|---|
| POST | `/auth/request-verification/` | Send 6-digit email verification code |
| POST | `/auth/verify-and-register/` | Verify code and create account |
| POST | `/auth/login/` | Email + password login |
| POST | `/auth/google/` | Google OAuth login / register |

### Resources
| Method | URL | Action |
|---|---|---|
| GET / POST | `/users/` | List all users / create user |
| GET / PATCH / DELETE | `/users/<id>/` | Get / update / delete user |
| GET / POST | `/songs/?user_id=` | List songs (optionally filtered by user) / create song |
| GET / PATCH / DELETE | `/songs/<id>/` | Get / update / delete song |
| POST | `/songs/<id>/share/` | Create or retrieve share link |
| GET | `/share/<token>/` | Access a shared song |
| GET / POST | `/requests/?user_id=` | List generation requests / submit new request |
| GET / PATCH | `/requests/<id>/` | Get / update generation request |
| GET / POST | `/feedback/` | List / submit feedback (internal) |

---

## Domain Models

| Model | Key Constraints |
|---|---|
| `User` | Dual auth: `google_id` OR `password_hash` (at least one required) |
| `Song` | Max 1 M songs/user; `audio_file_path` only set when status = `Completed` |
| `MusicGenerationRequest` | Title mandatory; `custom_story` ≤ 1 000 chars; 15-min generation timeout |
| `ShareLink` | OneToOne with `Song`; cascade-deleted with its parent |
| `Feedback` | Internal only; `Song` FK is optional |
| `EmailVerification` | Temporary; 6-digit code, expires in 10 minutes |

**Enumerations:** `Genre` (Pop · Rock · Jazz · Classical · Hip-Hop) · `Mood` · `Occasion` · `VoiceType` · `GenerationStatus`

---

## Django Admin

```bash
cd backend && python manage.py createsuperuser
```

Navigate to **http://127.0.0.1:8001/admin/** for full CRUD access across all models.

---

## Project Structure

```
cithara/
├── requirements.txt
├── backend/
│   ├── manage.py
│   ├── cithara/              # Django project (settings, urls)
│   └── domain/               # Models, views, admin, Suno service
│       ├── models.py
│       ├── views.py
│       ├── suno_service.py
│       └── migrations/
└── frontend/
    └── src/
        ├── app/              # Next.js App Router pages
        │   ├── dashboard/
        │   ├── songs/
        │   ├── users/
        │   ├── requests/
        │   └── share/[token]/
        ├── components/       # Shared UI components (AudioPlayer, …)
        ├── contexts/         # AuthContext
        └── lib/              # API client & TypeScript types
```
