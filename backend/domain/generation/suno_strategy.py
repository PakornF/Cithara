"""
Suno API Song Generator Strategy
===================================
Implements SongGenerationStrategy by calling the SunoAPI.org external service.

Flow:
  1. POST /api/v1/generate  → receives taskId
  2. Poll GET /api/v1/generate/record-info?taskId=<id> until status == SUCCESS
  3. Extract audioUrl from sunoData[0] and return it

Configuration (via environment variables):
  SUNO_AI_API_KEY   – Bearer token for authentication (REQUIRED)
  SUNO_API_BASE_URL – API base URL (default: https://api.sunoapi.org)

Activate via: GENERATOR_STRATEGY=suno  (in environment or .env)
"""

import time
import requests
from django.conf import settings

from .interface import GenerationRequest, GenerationResult, SongGenerationStrategy

# Polling configuration
POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 60  # 60 × 5s = 5 minutes max

# Suno API status values
STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED_STATES = {"CREATE_TASK_FAILED", "GENERATE_AUDIO_FAILED"}


class SunoSongGeneratorStrategy(SongGenerationStrategy):
    """
    Calls the SunoAPI.org service to generate a real AI song.

    Requires SUNO_AI_API_KEY to be set in the environment / Django settings.
    Uses polling (not callbacks) to retrieve the final audio URL.
    """

    def __init__(self):
        self._api_key: str = getattr(settings, "SUNO_AI_API_KEY", "") or ""
        self._base_url: str = (
            getattr(settings, "SUNO_API_BASE_URL", "https://api.sunoapi.org")
            .rstrip("/")
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Full generation flow: submit → poll → return audio URL.
        """
        if not self._api_key:
            return GenerationResult(
                success=False,
                error=(
                    "SUNO_AI_API_KEY is not configured. "
                    "Set it in your environment or .env file."
                ),
            )

        print(
            f"[SunoSongGeneratorStrategy] Submitting generation for "
            f"request_id={request.request_id}, title='{request.title}'"
        )

        # Step 1: Create the generation task
        task_id, error = self._create_task(request)
        if error:
            return GenerationResult(success=False, error=error)

        print(f"[SunoSongGeneratorStrategy] Task created: taskId={task_id}")

        # Step 2: Poll for completion
        audio_url, error = self._poll_for_result(task_id)
        if error:
            return GenerationResult(
                success=False,
                task_id=task_id,
                error=error,
            )

        print(f"[SunoSongGeneratorStrategy] Generation SUCCESS. audioUrl={audio_url}")

        return GenerationResult(
            success=True,
            audio_url=audio_url,
            task_id=task_id,
            metadata={"strategy": "suno", "title": request.title},
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _create_task(self, request: GenerationRequest):
        """
        POST to Suno's generate endpoint.
        Returns (task_id, None) on success or (None, error_message) on failure.
        """
        url = f"{self._base_url}/api/v1/generate"
        payload = {
            "customMode": False,
            "instrumental": False,
            "model": "V4_5",
            "prompt": f"{request.title}. {request.prompt}",
            "callBackUrl": "https://webhook.site/dummy",
        }

        try:
            resp = requests.post(url, json=payload, headers=self._headers, timeout=120)
            resp.raise_for_status()
            data = resp.json() or {}
            task_id = (data.get("data") or {}).get("taskId")
            if not task_id:
                return None, f"Suno API did not return a taskId. Response: {data}"
            return task_id, None
        except requests.HTTPError as exc:
            return None, f"Suno API HTTP error on task creation: {exc}"
        except requests.RequestException as exc:
            return None, f"Network error contacting Suno API: {exc}"

    def _poll_for_result(self, task_id: str):
        """
        Poll the record-info endpoint until status is SUCCESS or a terminal failure.
        Returns (audio_url, None) on success or (None, error_message) on failure/timeout.
        """
        url = f"{self._base_url}/api/v1/generate/record-info"

        for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
            time.sleep(POLL_INTERVAL_SECONDS)
            print(
                f"[SunoSongGeneratorStrategy] Polling attempt {attempt}/{MAX_POLL_ATTEMPTS} "
                f"for taskId={task_id}"
            )

            try:
                resp = requests.get(
                    url,
                    params={"taskId": task_id},
                    headers=self._headers,
                    timeout=15,
                )
                if not resp.ok:
                    # Non-fatal: keep polling on transient HTTP errors
                    print(
                        f"[SunoSongGeneratorStrategy] Poll returned HTTP {resp.status_code}, retrying…"
                    )
                    continue

                data = resp.json() or {}
                task_data = data.get("data") or {}
                status = task_data.get("status", "")

                print(f"[SunoSongGeneratorStrategy] Status={status}")

                if status == STATUS_SUCCESS:
                    audio_url = self._extract_audio_url(task_data)
                    if audio_url:
                        return audio_url, None
                    return None, "Generation succeeded but no audioUrl found in response."

                if status in STATUS_FAILED_STATES:
                    return None, f"Suno API returned terminal failure status: {status}"

            except requests.RequestException as exc:
                # Non-fatal: keep polling
                print(f"[SunoSongGeneratorStrategy] Poll network error: {exc}, retrying…")

        return None, (
            f"Timed out waiting for Suno generation after "
            f"{MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS} seconds (taskId={task_id})."
        )

    @staticmethod
    def _extract_audio_url(task_data: dict) -> str | None:
        """Extract the first available audio URL from a SUCCESS response."""
        response_data = task_data.get("response") or {}
        suno_data = response_data.get("sunoData") or []
        if suno_data and isinstance(suno_data, list):
            clip = suno_data[0] or {}
            return clip.get("audioUrl") or clip.get("streamAudioUrl")
        return None