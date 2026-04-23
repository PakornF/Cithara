"""
Tests for Exercise 4: Strategy Pattern
=========================================
Covers:
  - MockSongGeneratorStrategy produces a valid, deterministic result
  - SunoSongGeneratorStrategy fails gracefully when no API key is configured
  - SunoSongGeneratorStrategy calls the correct endpoints and parses SUCCESS
  - get_strategy() returns the correct class based on GENERATOR_STRATEGY setting
  - Strategy interface contract is satisfied by both concrete classes
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from domain.generation import (
    GenerationRequest,
    MockSongGeneratorStrategy,
    SunoSongGeneratorStrategy,
    get_strategy,
)
from domain.generation.interface import SongGenerationStrategy


# Helper: build a minimal GenerationRequest DTO
def _make_request(**kwargs):
    defaults = dict(
        request_id=1,
        title="Test Song",
        prompt="Style: Pop, Happy | Occasion/Theme: Birthday",
        genre="Pop",
        mood="Happy",
        voice_type="Female",
        occasion="Birthday",
    )
    defaults.update(kwargs)
    return GenerationRequest(**defaults)


# ---------------------------------------------------------------------------
# Interface / contract tests
# ---------------------------------------------------------------------------

class TestStrategyInterface(TestCase):
    """Both concrete strategies must satisfy the SongGenerationStrategy interface."""

    def test_mock_is_strategy(self):
        self.assertIsInstance(MockSongGeneratorStrategy(), SongGenerationStrategy)

    def test_suno_is_strategy(self):
        self.assertIsInstance(SunoSongGeneratorStrategy(), SongGenerationStrategy)

    def test_mock_has_generate(self):
        self.assertTrue(callable(getattr(MockSongGeneratorStrategy(), "generate", None)))

    def test_suno_has_generate(self):
        self.assertTrue(callable(getattr(SunoSongGeneratorStrategy(), "generate", None)))


# ---------------------------------------------------------------------------
# Mock strategy tests
# ---------------------------------------------------------------------------

class TestMockSongGeneratorStrategy(TestCase):

    def setUp(self):
        self.strategy = MockSongGeneratorStrategy()

    def test_returns_success(self):
        result = self.strategy.generate(_make_request())
        self.assertTrue(result.success)

    def test_returns_audio_url(self):
        result = self.strategy.generate(_make_request())
        self.assertIsNotNone(result.audio_url)
        self.assertTrue(result.audio_url.startswith("http"))

    def test_returns_task_id(self):
        result = self.strategy.generate(_make_request())
        self.assertIsNotNone(result.task_id)
        self.assertIn("MOCK-", result.task_id)

    def test_deterministic_task_id(self):
        """Same request_id + title → same task_id every time."""
        r1 = self.strategy.generate(_make_request(request_id=42, title="Birthday"))
        r2 = self.strategy.generate(_make_request(request_id=42, title="Birthday"))
        self.assertEqual(r1.task_id, r2.task_id)

    def test_different_requests_different_task_ids(self):
        r1 = self.strategy.generate(_make_request(request_id=1, title="Song A"))
        r2 = self.strategy.generate(_make_request(request_id=2, title="Song B"))
        self.assertNotEqual(r1.task_id, r2.task_id)

    def test_error_is_none_on_success(self):
        result = self.strategy.generate(_make_request())
        self.assertIsNone(result.error)

    def test_metadata_contains_strategy_key(self):
        result = self.strategy.generate(_make_request())
        self.assertEqual(result.metadata.get("strategy"), "mock")


# ---------------------------------------------------------------------------
# Suno strategy tests
# ---------------------------------------------------------------------------

class TestSunoSongGeneratorStrategyNoKey(TestCase):
    """Without an API key the strategy should fail gracefully."""

    @override_settings(SUNO_AI_API_KEY="")
    def test_fails_without_api_key(self):
        strategy = SunoSongGeneratorStrategy()
        result = strategy.generate(_make_request())
        self.assertFalse(result.success)
        self.assertIn("SUNO_AI_API_KEY", result.error)


class TestSunoSongGeneratorStrategyWithMockedAPI(TestCase):
    """Mock the HTTP layer to test the strategy's logic end-to-end."""

    FAKE_TASK_ID = "abc123"
    FAKE_AUDIO_URL = "https://cdn.sunoapi.org/audio/fake.mp3"

    def _make_create_response(self):
        mock = MagicMock()
        mock.ok = True
        mock.raise_for_status = MagicMock()
        mock.json.return_value = {"data": {"taskId": self.FAKE_TASK_ID}}
        return mock

    def _make_poll_success_response(self):
        mock = MagicMock()
        mock.ok = True
        mock.json.return_value = {
            "data": {
                "status": "SUCCESS",
                "response": {
                    "sunoData": [{"audioUrl": self.FAKE_AUDIO_URL}]
                },
            }
        }
        return mock

    def _make_poll_pending_response(self):
        mock = MagicMock()
        mock.ok = True
        mock.json.return_value = {"data": {"status": "PENDING"}}
        return mock

    @override_settings(SUNO_AI_API_KEY="test-key-123")
    @patch("domain.generation.suno_strategy.requests.get")
    @patch("domain.generation.suno_strategy.requests.post")
    @patch("domain.generation.suno_strategy.time.sleep", return_value=None)
    def test_successful_generation(self, mock_sleep, mock_post, mock_get):
        mock_post.return_value = self._make_create_response()
        mock_get.return_value = self._make_poll_success_response()

        strategy = SunoSongGeneratorStrategy()
        result = strategy.generate(_make_request())

        self.assertTrue(result.success)
        self.assertEqual(result.audio_url, self.FAKE_AUDIO_URL)
        self.assertEqual(result.task_id, self.FAKE_TASK_ID)
        self.assertIsNone(result.error)

    @override_settings(SUNO_AI_API_KEY="test-key-123")
    @patch("domain.generation.suno_strategy.requests.get")
    @patch("domain.generation.suno_strategy.requests.post")
    @patch("domain.generation.suno_strategy.time.sleep", return_value=None)
    def test_polls_until_success(self, mock_sleep, mock_post, mock_get):
        """Strategy should keep polling through PENDING before getting SUCCESS."""
        mock_post.return_value = self._make_create_response()
        mock_get.side_effect = [
            self._make_poll_pending_response(),
            self._make_poll_pending_response(),
            self._make_poll_success_response(),
        ]

        strategy = SunoSongGeneratorStrategy()
        result = strategy.generate(_make_request())

        self.assertTrue(result.success)
        self.assertEqual(mock_get.call_count, 3)

    @override_settings(SUNO_AI_API_KEY="test-key-123")
    @patch("domain.generation.suno_strategy.requests.get")
    @patch("domain.generation.suno_strategy.requests.post")
    @patch("domain.generation.suno_strategy.time.sleep", return_value=None)
    def test_terminal_failure_status(self, mock_sleep, mock_post, mock_get):
        mock_post.return_value = self._make_create_response()
        failed_resp = MagicMock()
        failed_resp.ok = True
        failed_resp.json.return_value = {"data": {"status": "GENERATE_AUDIO_FAILED"}}
        mock_get.return_value = failed_resp

        strategy = SunoSongGeneratorStrategy()
        result = strategy.generate(_make_request())

        self.assertFalse(result.success)
        self.assertIn("GENERATE_AUDIO_FAILED", result.error)

    @override_settings(SUNO_AI_API_KEY="test-key-123")
    @patch("domain.generation.suno_strategy.requests.post")
    @patch("domain.generation.suno_strategy.time.sleep", return_value=None)
    def test_no_task_id_in_response(self, mock_sleep, mock_post):
        bad_resp = MagicMock()
        bad_resp.raise_for_status = MagicMock()
        bad_resp.json.return_value = {"data": {}}
        mock_post.return_value = bad_resp

        strategy = SunoSongGeneratorStrategy()
        result = strategy.generate(_make_request())

        self.assertFalse(result.success)
        self.assertIn("taskId", result.error)


# ---------------------------------------------------------------------------
# Strategy selector tests
# ---------------------------------------------------------------------------

class TestGetStrategy(TestCase):

    @override_settings(GENERATOR_STRATEGY="mock")
    def test_returns_mock_when_set(self):
        self.assertIsInstance(get_strategy(), MockSongGeneratorStrategy)

    @override_settings(GENERATOR_STRATEGY="suno")
    def test_returns_suno_when_set(self):
        self.assertIsInstance(get_strategy(), SunoSongGeneratorStrategy)

    @override_settings(GENERATOR_STRATEGY="MOCK")
    def test_case_insensitive_mock(self):
        self.assertIsInstance(get_strategy(), MockSongGeneratorStrategy)

    @override_settings(GENERATOR_STRATEGY="SUNO")
    def test_case_insensitive_suno(self):
        self.assertIsInstance(get_strategy(), SunoSongGeneratorStrategy)

    @override_settings(GENERATOR_STRATEGY="unknown_value")
    def test_falls_back_to_mock_on_unknown(self):
        self.assertIsInstance(get_strategy(), MockSongGeneratorStrategy)

    @override_settings(GENERATOR_STRATEGY="")
    def test_falls_back_to_mock_on_empty(self):
        self.assertIsInstance(get_strategy(), MockSongGeneratorStrategy)
