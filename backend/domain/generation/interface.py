"""
Song Generation Strategy Interface
====================================
Defines the common contract that all song-generation strategies must implement.
Following the Strategy design pattern, every strategy:
  - Accepts a GenerationRequest (input DTO)
  - Returns a GenerationResult (output DTO)
  - Can raise exceptions on unrecoverable errors

The rest of the system only depends on this interface, never on a concrete class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GenerationRequest:
    """
    Input data transfer object for a song generation request.
    Decouples strategy logic from the Django ORM model.
    """
    request_id: int
    title: str
    prompt: str
    genre: str = ''
    mood: str = ''
    voice_type: str = ''
    occasion: str = ''
    custom_story: Optional[str] = None


@dataclass
class GenerationResult:
    """
    Output data transfer object returned by every generation strategy.
    On success:  audio_url is populated, task_id may be populated, error is None.
    On failure:  audio_url is None, error describes what went wrong.
    """
    success: bool
    audio_url: Optional[str] = None
    task_id: Optional[str] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class SongGenerationStrategy(ABC):
    """
    Abstract base class for all song-generation strategies.

    Subclasses must implement `generate(request) -> GenerationResult`.
    """

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate a song based on the given request.

        Args:
            request: A GenerationRequest containing all inputs needed for generation.

        Returns:
            A GenerationResult with success status and either an audio_url or an error.

        Raises:
            Exception: May raise on truly unexpected errors; callers should handle.
        """
        ...

    def __str__(self) -> str:
        return self.__class__.__name__
