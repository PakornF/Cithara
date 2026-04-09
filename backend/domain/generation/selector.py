"""
Strategy Selector
==================
Single point of truth for choosing the active song-generation strategy.

Reads GENERATOR_STRATEGY from the environment (or Django settings) and
returns the appropriate concrete strategy instance.

Supported values (case-insensitive):
  mock   → MockSongGeneratorStrategy  (default when key is missing or unknown)
  suno   → SunoSongGeneratorStrategy

Usage:
    from domain.generation import get_strategy

    strategy = get_strategy()
    result = strategy.generate(request)

Never import a concrete strategy class directly from application code –
always go through get_strategy() so the selection remains centralised.
"""

import os
from django.conf import settings

from .interface import SongGenerationStrategy
from .mock_strategy import MockSongGeneratorStrategy
from .suno_strategy import SunoSongGeneratorStrategy


def get_strategy() -> SongGenerationStrategy:
    """
    Factory function: reads GENERATOR_STRATEGY and returns the active strategy.

    Precedence:
        1. Django settings.GENERATOR_STRATEGY  (set in settings.py / env)
        2. GENERATOR_STRATEGY environment variable (fallback)
        3. 'mock' if neither is set

    Returns:
        An instance of a SongGenerationStrategy subclass.
    """
    raw = (
        getattr(settings, "GENERATOR_STRATEGY", None) or "mock"
    ).strip().lower()

    if raw == "suno":
        strategy = SunoSongGeneratorStrategy()
    else:
        if raw not in ("mock",):
            print(
                f"[get_strategy] Unknown GENERATOR_STRATEGY='{raw}'. "
                f"Falling back to 'mock'."
            )
        strategy = MockSongGeneratorStrategy()

    print(f"[get_strategy] Active strategy: {strategy}")
    return strategy