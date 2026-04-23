"""
Generation Service (Orchestrator)
====================================
This module is the only place that knows about the Django ORM *and* triggers
a generation strategy.  It:

  1. Loads the MusicGenerationRequest from the database.
  2. Builds a GenerationRequest DTO.
  3. Calls get_strategy().generate(dto).
  4. Persists the result (Song / status) back to the database.

The concrete strategy is chosen by get_strategy() based on the
GENERATOR_STRATEGY environment variable – never hard-coded here.
"""

import threading

from .generation import GenerationRequest, get_strategy
from .models import GenerationStatus, MusicGenerationRequest, Song


# ---------------------------------------------------------------------------
# Prompt builder (unchanged from Exercise 3)
# ---------------------------------------------------------------------------

def _build_prompt(req: MusicGenerationRequest) -> str:
    parts = []
    if req.custom_story:
        parts.append(req.custom_story)

    style_parts = []
    if req.genre:
        style_parts.append(req.genre)
    if req.mood:
        style_parts.append(req.mood)
    if req.voice_type:
        style_parts.append(req.voice_type)

    if style_parts:
        parts.append(f"Style: {', '.join(style_parts)}")

    if req.occasion:
        parts.append(f"Occasion/Theme: {req.occasion}")

    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Core task – runs in a background thread
# ---------------------------------------------------------------------------

def generate_song_task(req_id: int) -> None:
    """
    Background worker: load → build DTO → delegate to strategy → persist result.
    """
    try:
        req = MusicGenerationRequest.objects.get(pk=req_id)
    except MusicGenerationRequest.DoesNotExist:
        return

    # Mark as in-progress
    req.status = GenerationStatus.INPROGRESS
    req.error_message = None
    req.save(update_fields=["status", "error_message"])

    # Build the prompt and persist it
    prompt = _build_prompt(req)
    req.prompt_generated = prompt
    req.save(update_fields=["prompt_generated"])

    # Resolve the active strategy (mock | suno) from settings/env
    strategy = get_strategy()

    # Build the input DTO
    generation_request = GenerationRequest(
        request_id=req.id,
        title=req.title,
        prompt=prompt,
        genre=req.genre,
        mood=req.mood,
        voice_type=req.voice_type,
        occasion=req.occasion,
        custom_story=req.custom_story,
    )

    # Delegate to the strategy
    result = strategy.generate(generation_request)

    # Persist the result
    if result.success and result.audio_url:
        song = Song.objects.create(
            owner=req.user,
            title=req.title,
            genre=req.genre,
            mood=req.mood,
            occasion=req.occasion,
            voice_type=req.voice_type,
            status=GenerationStatus.COMPLETED,
            audio_file_path=result.audio_url,
            prompt_used=prompt,
        )
        req.song = song
        req.status = GenerationStatus.COMPLETED
        req.save(update_fields=["song", "status"])
    else:
        req.status = GenerationStatus.FAILED
        req.error_message = result.error or "Unknown error during generation."
        req.save(update_fields=["status", "error_message"])


# ---------------------------------------------------------------------------
# Public API – launch a background thread
# ---------------------------------------------------------------------------

def launch_generation_thread(req_id: int) -> None:
    """Spin up a daemon thread to run generate_song_task without blocking the request."""
    t = threading.Thread(target=generate_song_task, args=(req_id,))
    t.daemon = True
    t.start()
