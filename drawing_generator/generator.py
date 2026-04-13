"""Core drawing number generation engine.

Manages sequence counters per discipline, generates new drawing numbers,
and handles revision workflows. Designed to be backed by an EPDM vault
connection in production; uses in-memory state for demonstration.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import AsyncIterator, Optional

from drawing_generator.models import (
    Discipline,
    DrawingConfig,
    DrawingNumber,
    GenerationResult,
)


class DrawingNumberError(Exception):
    """Base exception for drawing number generation failures."""


class SequenceExhaustedError(DrawingNumberError):
    """Raised when the sequence counter exceeds the configured maximum."""

    def __init__(self, discipline: Discipline, max_seq: int) -> None:
        self.discipline = discipline
        self.max_sequence = max_seq
        super().__init__(
            f"Sequence exhausted for discipline {discipline.name}: "
            f"maximum {max_seq} reached"
        )


class DuplicateDrawingError(DrawingNumberError):
    """Raised when attempting to register a drawing number that already exists."""

    def __init__(self, drawing_number: DrawingNumber) -> None:
        self.drawing_number = drawing_number
        super().__init__(f"Drawing {drawing_number.formatted} already exists")


class RevisionError(DrawingNumberError):
    """Raised on invalid revision operations."""


class DrawingNumberGenerator:
    """Generates and tracks engineering drawing numbers.

    Maintains per-discipline sequence counters and a registry of all
    issued drawing numbers. In production, this would interface with
    the EPDM vault API; here it uses in-memory storage.

    Args:
        config: Generator configuration.
    """

    def __init__(self, config: DrawingConfig) -> None:
        self._config = config
        self._sequences: dict[Discipline, int] = defaultdict(int)
        self._registry: dict[str, DrawingNumber] = {}
        self._lock = asyncio.Lock()

    @property
    def config(self) -> DrawingConfig:
        """The active generator configuration."""
        return self._config

    @property
    def registry(self) -> dict[str, DrawingNumber]:
        """Read-only view of the drawing number registry."""
        return dict(self._registry)

    def get_next_sequence(self, discipline: Discipline) -> int:
        """Advance and return the next sequence number for a discipline.

        Args:
            discipline: The engineering discipline.

        Returns:
            The next available sequence number.

        Raises:
            SequenceExhaustedError: If the maximum sequence is reached.
        """
        current = self._sequences[discipline]
        next_seq = current + 1
        if next_seq > self._config.max_sequence:
            raise SequenceExhaustedError(discipline, self._config.max_sequence)
        self._sequences[discipline] = next_seq
        return next_seq

    def generate(self, discipline: Discipline) -> GenerationResult:
        """Generate a new drawing number for the given discipline.

        Args:
            discipline: Engineering discipline code.

        Returns:
            GenerationResult with the new drawing number and vault path.
        """
        seq = self.get_next_sequence(discipline)
        drawing = DrawingNumber(
            prefix=self._config.project_prefix,
            discipline=discipline,
            sequence=seq,
            revision=self._config.default_revision,
        )

        if drawing.formatted in self._registry:
            raise DuplicateDrawingError(drawing)

        self._registry[drawing.formatted] = drawing
        vault_path = self._build_vault_path(drawing)

        return GenerationResult(
            drawing_number=drawing,
            is_new=True,
            previous=None,
            vault_path=vault_path,
        )

    def revise(self, drawing_number: str) -> GenerationResult:
        """Create a new revision of an existing drawing.

        Args:
            drawing_number: The formatted drawing number string to revise.

        Returns:
            GenerationResult with the revised drawing number.

        Raises:
            RevisionError: If the drawing doesn't exist or can't be revised.
        """
        normalized = drawing_number.strip().upper()
        existing = self._registry.get(normalized)
        if existing is None:
            raise RevisionError(
                f"Cannot revise '{normalized}': not found in registry"
            )

        try:
            revised = existing.next_revision()
        except ValueError as exc:
            raise RevisionError(str(exc)) from exc

        if revised.formatted in self._registry:
            raise DuplicateDrawingError(revised)

        self._registry[revised.formatted] = revised
        vault_path = self._build_vault_path(revised)

        return GenerationResult(
            drawing_number=revised,
            is_new=False,
            previous=existing,
            vault_path=vault_path,
        )

    async def async_generate(self, discipline: Discipline) -> GenerationResult:
        """Thread-safe async drawing number generation.

        Acquires an async lock before modifying shared state,
        suitable for concurrent EPDM vault operations.

        Args:
            discipline: Engineering discipline code.

        Returns:
            GenerationResult with the new drawing number.
        """
        async with self._lock:
            # Simulate EPDM vault latency
            await asyncio.sleep(0.01)
            return self.generate(discipline)

    async def async_generate_batch(
        self,
        discipline: Discipline,
        count: int,
    ) -> AsyncIterator[GenerationResult]:
        """Async generator yielding multiple drawing numbers.

        Args:
            discipline: Engineering discipline code.
            count: Number of drawing numbers to generate.

        Yields:
            GenerationResult for each generated drawing number.
        """
        for _ in range(count):
            result = await self.async_generate(discipline)
            yield result

    def bulk_generate(
        self,
        discipline: Discipline,
        count: int,
    ) -> list[GenerationResult]:
        """Generate multiple drawing numbers synchronously.

        Args:
            discipline: Engineering discipline code.
            count: Number of drawing numbers to generate.

        Returns:
            List of GenerationResult objects.

        Raises:
            ValueError: If count is not positive.
        """
        if count < 1:
            raise ValueError(f"Count must be positive, got {count}")
        return [self.generate(discipline) for _ in range(count)]

    def lookup(self, drawing_number: str) -> Optional[DrawingNumber]:
        """Look up a drawing number in the registry.

        Args:
            drawing_number: The formatted drawing number string.

        Returns:
            The DrawingNumber if found, else None.
        """
        return self._registry.get(drawing_number.strip().upper())

    def get_discipline_count(self, discipline: Discipline) -> int:
        """Return the count of drawings issued for a discipline.

        Args:
            discipline: The engineering discipline.

        Returns:
            Number of drawings generated for the discipline.
        """
        return self._sequences.get(discipline, 0)

    def _build_vault_path(self, drawing: DrawingNumber) -> str:
        """Construct the simulated EPDM vault file path.

        Args:
            drawing: The drawing number to build a path for.

        Returns:
            Vault-style file path string.
        """
        return (
            f"/{self._config.epdm_vault}/{self._config.project_prefix}/"
            f"{drawing.discipline.name}/{drawing.formatted}.slddrw"
        )
