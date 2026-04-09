"""
Mock Song Generator Strategy
==============================
Implements SongGenerationStrategy for offline / test environments.

Behaviour:
- Never calls any external API.
- Returns a predictable, fixed audio URL and a deterministic fake task ID.
- Useful for development, CI, and unit testing without network access.

Activate via: GENERATOR_STRATEGY=mock  (in environment or .env)
"""

import hashlib
import time

from .interface import GenerationRequest, GenerationResult, SongGenerationStrategy


class MockSongGeneratorStrategy(SongGenerationStrategy):
    """
    Offline, deterministic strategy that produces predictable fake output.
    No network calls are made.
    """

    # Public placeholder audio file hosted on a CDN – always reachable
    MOCK_AUDIO_URL = (
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    )

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Return a deterministic mock result immediately.

        The task_id is derived from request_id so repeated calls for the same
        request always yield the same fake ID (useful for idempotency tests).
        """
        print(
            f"[MockSongGeneratorStrategy] Generating mock song for "
            f"request_id={request.request_id}, title='{request.title}'"
        )

        # Simulate a brief processing delay (makes demo logs more realistic)
        time.sleep(1)

        # Deterministic fake task ID based on the request
        raw = f"mock-{request.request_id}-{request.title}"
        fake_task_id = "MOCK-" + hashlib.md5(raw.encode()).hexdigest()[:12].upper()

        print(
            f"[MockSongGeneratorStrategy] Done. task_id={fake_task_id}, "
            f"audio_url={self.MOCK_AUDIO_URL}"
        )

        return GenerationResult(
            success=True,
            audio_url=self.MOCK_AUDIO_URL,
            task_id=fake_task_id,
            metadata={
                "strategy": "mock",
                "title": request.title,
                "genre": request.genre,
                "mood": request.mood,
                "voice_type": request.voice_type,
                "occasion": request.occasion,
            },
        )
