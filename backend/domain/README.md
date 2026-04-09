# Cithara Backend — Exercise 4: Strategy Pattern

## Overview

This exercise applies the **Strategy design pattern** to song generation. The generation
behaviour is fully swappable at runtime via a single environment variable —
no code changes required to switch between backends.

---

## Architecture

```
domain/generation/
├── __init__.py          # Package exports
├── interface.py         # SongGenerationStrategy (ABC) + GenerationRequest / GenerationResult DTOs
├── mock_strategy.py     # MockSongGeneratorStrategy  — offline, deterministic
├── suno_strategy.py     # SunoSongGeneratorStrategy  — calls sunoapi.org
└── selector.py          # get_strategy() — single selection point (reads GENERATOR_STRATEGY)

domain/suno_service.py   # Thin orchestrator: ORM → DTO → strategy → ORM
```

### Pattern structure

| Role | Class |
|---|---|
| Strategy interface | `SongGenerationStrategy` (ABC) |
| Concrete Strategy A | `MockSongGeneratorStrategy` |
| Concrete Strategy B | `SunoSongGeneratorStrategy` |
| Context / Orchestrator | `generate_song_task()` in `suno_service.py` |
| Strategy selector | `get_strategy()` in `selector.py` |

The orchestrator **never imports a concrete strategy directly**.
It always calls `get_strategy()`, which is the only place that resolves the active backend.

---

## Running in Mock Mode

Mock mode is the **default** — no API key or network access needed.

```bash
# Explicit (or just omit GENERATOR_STRATEGY entirely)
GENERATOR_STRATEGY=mock python manage.py runserver
```

### Demo command (no running server needed)

```bash
GENERATOR_STRATEGY=mock python manage.py demo_generation
# With custom title:
GENERATOR_STRATEGY=mock python manage.py demo_generation --title "My Birthday Song"
```

Example output:
```
[get_strategy] Active strategy: MockSongGeneratorStrategy

=== Active strategy: MockSongGeneratorStrategy ===
Submitting generation request…
[MockSongGeneratorStrategy] Generating mock song for request_id=0, title='My Birthday Song'
[MockSongGeneratorStrategy] Done. task_id=MOCK-92D8BC4D1BB9, audio_url=https://www.soundhelix.com/…

✔ Generation succeeded!
  task_id  : MOCK-92D8BC4D1BB9
  audio_url: https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3
  metadata : {'strategy': 'mock', 'title': 'My Birthday Song', ...}
```

### Via the API (POST /requests/)

```bash
# Start server in mock mode
GENERATOR_STRATEGY=mock python manage.py runserver

# Create a user first (if you don't already have one)
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","name":"Demo User","password_hash":"dev-only"}'

# Submit a generation request (replace user_id with an existing user)
curl -X POST http://localhost:8000/requests/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "title": "Birthday Song", "genre": "Pop", "mood": "Happy", "voice_type": "Female", "occasion": "Birthday"}'

# Poll for result
curl http://localhost:8000/requests/<id>/
```

---

## Running in Suno Mode

### Where to put the API key

**Never commit the API key to the repository.**

Set it as an environment variable or in a `.env` file (add `.env` to `.gitignore`):

```bash
# .env  (do NOT commit this file)
SUNO_AI_API_KEY=your_actual_key_here
GENERATOR_STRATEGY=suno
```

Then run:
```bash
export $(cat .env | xargs)
python manage.py runserver
```

Or inline:
```bash
GENERATOR_STRATEGY=suno SUNO_AI_API_KEY=your_key python manage.py runserver
```

### Demo command

```bash
GENERATOR_STRATEGY=suno SUNO_AI_API_KEY=your_key python manage.py demo_generation --title "My Suno Song"
```

Example output:
```
[get_strategy] Active strategy: SunoSongGeneratorStrategy

=== Active strategy: SunoSongGeneratorStrategy ===
Submitting generation request…
[SunoSongGeneratorStrategy] Submitting generation for request_id=0, title='My Suno Song'
[SunoSongGeneratorStrategy] Task created: taskId=<uuid>
[SunoSongGeneratorStrategy] Polling attempt 1/60 for taskId=<uuid>
[SunoSongGeneratorStrategy] Status=PENDING
...
[SunoSongGeneratorStrategy] Status=SUCCESS
[SunoSongGeneratorStrategy] Generation SUCCESS. audioUrl=https://...

✔ Generation succeeded!
  task_id  : <uuid>
  audio_url: https://cdn.sunoapi.org/audio/...
```

---

## Running Tests

```bash
python manage.py test domain.tests_strategy --verbosity=2
```

22 tests covering:
- Strategy interface contract (both classes are `SongGenerationStrategy` subclasses)
- `MockSongGeneratorStrategy` — success, determinism, metadata
- `SunoSongGeneratorStrategy` — no API key, HTTP mocking, polling, terminal failure
- `get_strategy()` selector — mock/suno/case-insensitive/unknown fallback

---

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

`requirements.txt` must include:
```
django
django-cors-headers
requests
certifi
```
