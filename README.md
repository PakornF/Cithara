# Cithara 🎵

> AI-powered song generation — create, manage, and share personalised music in seconds.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 5, SQLite (dev) |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **AI Generation** | Suno AI via sunoapi.org (strategy pattern: mock or real) |
| **Auth** | Email + verification code · Google OAuth (JWT) |

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+

### 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Edit `backend/.env`:

| Variable | How to get it |
|---|---|
| `EMAIL_HOST` | Your SMTP server (e.g. `smtp.gmail.com`). Leave blank to print codes to terminal instead. |
| `EMAIL_HOST_USER` | Your sender email address |
| `EMAIL_HOST_PASSWORD` | Gmail: enable 2FA → create an [App Password](https://myaccount.google.com/apppasswords) |
| `GENERATOR_STRATEGY` | `mock` (no key needed) or `suno` (real AI — see Running section) |
| `SUNO_AI_API_KEY` | Sign up at [sunoapi.org](https://sunoapi.org) and copy your API key. **Required only when `GENERATOR_STRATEGY=suno`.** |

> **Never commit your `.env` file.** It is already listed in `.gitignore`.

Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver 8001
```

Backend runs at **http://127.0.0.1:8001**

### 2. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env.local
```

Edit `frontend/.env.local`:

| Variable | How to get it |
|---|---|
| `NEXT_PUBLIC_API_URL` | Leave as `http://127.0.0.1:8001` for local development |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials → Create OAuth 2.0 Client ID (Web application). Add `http://localhost:3000` as an authorised origin. |

Start the dev server:

```bash
npm run dev
```

Frontend runs at **http://localhost:3000**

---

## Running the App

Both the backend and frontend must be running at the same time.

### Mock mode (default — no API key required)

Set in `backend/.env`:

```
GENERATOR_STRATEGY=mock
```

Then start both servers:

```bash
# Terminal 1 — backend
cd backend && source venv/bin/activate && python manage.py runserver 8001

# Terminal 2 — frontend
cd frontend && npm run dev
```

The mock strategy returns a fixed placeholder audio URL immediately — no network call to Suno is made. Useful for development and testing.

**Expected Django terminal output when a song is generated:**

```
[get_strategy] Active strategy: MockSongGeneratorStrategy
[MockSongGeneratorStrategy] Generating mock song for request_id=1, title='My Song'
[MockSongGeneratorStrategy] Done. task_id=MOCK-XXXXXXXXXXXX, audio_url=https://...
```

### Suno mode (real AI generation)

1. Sign up at [sunoapi.org](https://sunoapi.org) and copy your API key.
2. Set in `backend/.env`:

```
GENERATOR_STRATEGY=suno
SUNO_AI_API_KEY=your_api_key_here
```

3. Restart the backend server, then start both servers as above.

The Suno strategy:
1. POSTs to `https://api.sunoapi.org/api/v1/generate` to create a generation task.
2. Polls `GET /api/v1/generate/record-info?taskId=<id>` every 5 seconds (up to 5 minutes) until status is `SUCCESS`.
3. Saves the returned `audioUrl` to the song record.

**Expected Django terminal output:**

```
[get_strategy] Active strategy: SunoSongGeneratorStrategy
[SunoSongGeneratorStrategy] Submitting generation for request_id=1, title='My Song'
[SunoSongGeneratorStrategy] Task created: taskId=abc123...
[SunoSongGeneratorStrategy] Polling attempt 1/60 for taskId=abc123...
...
[SunoSongGeneratorStrategy] Generation SUCCESS. audioUrl=https://...
```

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `EMAIL_HOST` | _(empty)_ | SMTP host. If blank, codes print to terminal. |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_USE_TLS` | `true` | Use TLS |
| `EMAIL_HOST_USER` | _(empty)_ | Sender email |
| `EMAIL_HOST_PASSWORD` | _(empty)_ | SMTP password / App password |
| `DEFAULT_FROM_EMAIL` | `Cithara <noreply@cithara.local>` | From header |
| `GENERATOR_STRATEGY` | `mock` | `mock` or `suno` |
| `SUNO_AI_API_KEY` | _(empty)_ | Required when strategy is `suno` |
| `SUNO_API_BASE_URL` | `https://api.sunoapi.org` | Suno API base URL |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8001` | Django backend URL |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | _(empty)_ | Google OAuth client ID |

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
| GET / POST | `/songs/?user_id=` | List songs (optionally filtered by user) |
| GET / PATCH / DELETE | `/songs/<id>/` | Get / update / delete song |
| POST | `/songs/<id>/share/` | Create or retrieve share link |
| GET | `/share/<token>/` | Access a shared song |
| GET / POST | `/requests/?user_id=` | List generation requests / submit new request |
| GET / PATCH | `/requests/<id>/` | Get / update generation request |

---

## Domain Models

| Model | Key Constraints |
|---|---|
| `User` | Dual auth: `google_id` OR `password_hash` (at least one required) |
| `Song` | Max 1 M songs/user; `audio_file_path` only set when status = `Completed` |
| `MusicGenerationRequest` | Title mandatory; `custom_story` ≤ 1 000 chars; 15-min generation timeout |
| `ShareLink` | OneToOne with `Song`; cascade-deleted with its parent |
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
├── backend/
│   ├── manage.py
│   ├── .env.example
│   ├── requirements.txt
│   ├── cithara/                  # Django project (settings, urls)
│   └── domain/
│       ├── models/               # One file per model
│       ├── views.py              # All CRUD endpoints
│       ├── urls.py
│       ├── suno_service.py       # Async generation orchestrator
│       ├── generation/           # Strategy pattern
│       │   ├── interface.py      # SongGenerationStrategy ABC
│       │   ├── mock_strategy.py  # MockSongGeneratorStrategy
│       │   ├── suno_strategy.py  # SunoSongGeneratorStrategy
│       │   └── selector.py       # get_strategy() — reads GENERATOR_STRATEGY
│       └── migrations/
└── frontend/
    ├── .env.example
    └── src/
        ├── app/                  # Next.js App Router pages
        ├── components/           # AudioPlayer, etc.
        ├── contexts/             # AuthContext
        └── lib/                  # API client & TypeScript types
```
