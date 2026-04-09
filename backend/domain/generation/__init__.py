"""Song generation strategy package."""

from .interface import SongGenerationStrategy, GenerationRequest, GenerationResult
from .mock_strategy import MockSongGeneratorStrategy
from .suno_strategy import SunoSongGeneratorStrategy
from .selector import get_strategy

__all__ = [
    'SongGenerationStrategy',
    'GenerationRequest',
    'GenerationResult',
    'MockSongGeneratorStrategy',
    'SunoSongGeneratorStrategy',
    'get_strategy',
]
