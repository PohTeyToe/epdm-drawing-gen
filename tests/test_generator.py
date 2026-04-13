"""Comprehensive test suite for the drawing number generator.

Covers: generation, sequencing, revisions, parsing, validation,
async operations, bulk generation, config loading, and edge cases.
"""

from __future__ import annotations

import asyncio
import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from drawing_generator.config import load_config
from drawing_generator.generator import (
    DrawingNumberGenerator,
    DuplicateDrawingError,
    RevisionError,
    SequenceExhaustedError,
)
from drawing_generator.models import (
    Discipline,
    DrawingConfig,
    DrawingNumber,
    GenerationResult,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config() -> DrawingConfig:
    """Standard test configuration."""
    return DrawingConfig(project_prefix="MS")


@pytest.fixture
def generator(config: DrawingConfig) -> DrawingNumberGenerator:
    """Fresh generator instance for each test."""
    return DrawingNumberGenerator(config)


# ---------------------------------------------------------------------------
# Drawing number generation
# ---------------------------------------------------------------------------

class TestGeneration:
    """Tests for basic drawing number generation."""

    def test_generate_electrical(self, generator: DrawingNumberGenerator) -> None:
        result = generator.generate(Discipline.ELECTRICAL)
        assert result.drawing_number.formatted == "MS-E-0001-A"
        assert result.is_new is True
        assert result.previous is None

    def test_generate_mechanical(self, generator: DrawingNumberGenerator) -> None:
        result = generator.generate(Discipline.MECHANICAL)
        assert result.drawing_number.formatted == "MS-M-0001-A"

    def test_generate_optical(self, generator: DrawingNumberGenerator) -> None:
        result = generator.generate(Discipline.OPTICAL)
        assert result.drawing_number.formatted == "MS-O-0001-A"

    def test_generate_structural(self, generator: DrawingNumberGenerator) -> None:
        result = generator.generate(Discipline.STRUCTURAL)
        assert result.drawing_number.formatted == "MS-S-0001-A"

    def test_vault_path_format(self, generator: DrawingNumberGenerator) -> None:
        result = generator.generate(Discipline.ELECTRICAL)
        assert result.vault_path == "/ProductionVault/MS/ELECTRICAL/MS-E-0001-A.slddrw"


# ---------------------------------------------------------------------------
# Sequence management
# ---------------------------------------------------------------------------

class TestSequencing:
    """Tests for sequence counter behavior."""

    def test_auto_increment(self, generator: DrawingNumberGenerator) -> None:
        r1 = generator.generate(Discipline.ELECTRICAL)
        r2 = generator.generate(Discipline.ELECTRICAL)
        r3 = generator.generate(Discipline.ELECTRICAL)
        assert r1.drawing_number.sequence == 1
        assert r2.drawing_number.sequence == 2
        assert r3.drawing_number.sequence == 3

    def test_independent_discipline_sequences(
        self, generator: DrawingNumberGenerator
    ) -> None:
        generator.generate(Discipline.ELECTRICAL)
        generator.generate(Discipline.ELECTRICAL)
        mech = generator.generate(Discipline.MECHANICAL)
        assert mech.drawing_number.sequence == 1
        assert generator.get_discipline_count(Discipline.ELECTRICAL) == 2
        assert generator.get_discipline_count(Discipline.MECHANICAL) == 1

    def test_sequence_exhaustion(self) -> None:
        config = DrawingConfig(project_prefix="MS", max_sequence=2)
        gen = DrawingNumberGenerator(config)
        gen.generate(Discipline.ELECTRICAL)
        gen.generate(Discipline.ELECTRICAL)
        with pytest.raises(SequenceExhaustedError) as exc_info:
            gen.generate(Discipline.ELECTRICAL)
        assert exc_info.value.discipline == Discipline.ELECTRICAL
        assert exc_info.value.max_sequence == 2


# ---------------------------------------------------------------------------
# Revision handling
# ---------------------------------------------------------------------------

class TestRevisions:
    """Tests for drawing revision workflows."""

    def test_revise_existing_drawing(
        self, generator: DrawingNumberGenerator
    ) -> None:
        original = generator.generate(Discipline.ELECTRICAL)
        revised = generator.revise("MS-E-0001-A")
        assert revised.drawing_number.revision == "B"
        assert revised.is_new is False
        assert revised.previous == original.drawing_number

    def test_revise_nonexistent_raises(
        self, generator: DrawingNumberGenerator
    ) -> None:
        with pytest.raises(RevisionError, match="not found"):
            generator.revise("MS-E-9999-A")

    def test_revision_z_limit(self, generator: DrawingNumberGenerator) -> None:
        drawing = DrawingNumber(
            prefix="MS",
            discipline=Discipline.ELECTRICAL,
            sequence=1,
            revision="Z",
        )
        with pytest.raises(ValueError, match="revision Z"):
            drawing.next_revision()

    def test_multiple_revisions(self, generator: DrawingNumberGenerator) -> None:
        generator.generate(Discipline.OPTICAL)
        rev_b = generator.revise("MS-O-0001-A")
        rev_c = generator.revise("MS-O-0001-B")
        assert rev_b.drawing_number.revision == "B"
        assert rev_c.drawing_number.revision == "C"
        assert rev_c.previous == rev_b.drawing_number


# ---------------------------------------------------------------------------
# Parsing & validation
# ---------------------------------------------------------------------------

class TestParsing:
    """Tests for drawing number string parsing."""

    @pytest.mark.parametrize(
        "input_str,expected_prefix,expected_disc,expected_seq,expected_rev",
        [
            ("MS-E-0001-A", "MS", Discipline.ELECTRICAL, 1, "A"),
            ("MS-M-0042-B", "MS", Discipline.MECHANICAL, 42, "B"),
            ("PROJ-S-1000-Z", "PROJ", Discipline.STRUCTURAL, 1000, "Z"),
            ("ms-o-0007-c", "MS", Discipline.OPTICAL, 7, "C"),
        ],
    )
    def test_parse_valid_formats(
        self,
        input_str: str,
        expected_prefix: str,
        expected_disc: Discipline,
        expected_seq: int,
        expected_rev: str,
    ) -> None:
        dn = DrawingNumber.parse(input_str)
        assert dn.prefix == expected_prefix
        assert dn.discipline == expected_disc
        assert dn.sequence == expected_seq
        assert dn.revision == expected_rev

    @pytest.mark.parametrize(
        "bad_input",
        [
            "",
            "INVALID",
            "MS-X-0001-A",      # bad discipline
            "MS-E-01-A",        # sequence too short
            "MS-E-0001-1",      # numeric revision
            "M-E-0001-A",       # prefix too short
            "ABCDE-E-0001-A",   # prefix too long
        ],
    )
    def test_parse_rejects_invalid(self, bad_input: str) -> None:
        with pytest.raises(ValueError, match="Invalid drawing number"):
            DrawingNumber.parse(bad_input)


# ---------------------------------------------------------------------------
# Model validation
# ---------------------------------------------------------------------------

class TestModelValidation:
    """Tests for Pydantic model constraints."""

    def test_config_rejects_short_prefix(self) -> None:
        with pytest.raises(ValidationError):
            DrawingConfig(project_prefix="X")

    def test_config_rejects_non_alpha_prefix(self) -> None:
        with pytest.raises(ValidationError):
            DrawingConfig(project_prefix="M-S")

    def test_config_accepts_numeric_prefix(self) -> None:
        config = DrawingConfig(project_prefix="M2")
        assert config.project_prefix == "M2"

    def test_config_normalizes_prefix_case(self) -> None:
        config = DrawingConfig(project_prefix="ms")
        assert config.project_prefix == "MS"

    def test_generation_result_revision_consistency(self) -> None:
        dn = DrawingNumber(
            prefix="MS",
            discipline=Discipline.ELECTRICAL,
            sequence=1,
            revision="B",
        )
        with pytest.raises(ValidationError, match="previous drawing"):
            GenerationResult(
                drawing_number=dn,
                is_new=False,
                previous=None,
                vault_path="/test",
            )

    def test_generation_result_new_with_previous_rejected(self) -> None:
        dn_a = DrawingNumber(
            prefix="MS", discipline=Discipline.ELECTRICAL, sequence=1, revision="A"
        )
        dn_b = DrawingNumber(
            prefix="MS", discipline=Discipline.ELECTRICAL, sequence=1, revision="B"
        )
        with pytest.raises(ValidationError, match="must not reference"):
            GenerationResult(
                drawing_number=dn_b,
                is_new=True,
                previous=dn_a,
                vault_path="/test",
            )


# ---------------------------------------------------------------------------
# Discipline enum
# ---------------------------------------------------------------------------

class TestDiscipline:
    """Tests for discipline resolution."""

    def test_from_code(self) -> None:
        assert Discipline.from_string("E") == Discipline.ELECTRICAL

    def test_from_name(self) -> None:
        assert Discipline.from_string("mechanical") == Discipline.MECHANICAL

    def test_case_insensitive(self) -> None:
        assert Discipline.from_string("o") == Discipline.OPTICAL

    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown discipline"):
            Discipline.from_string("X")


# ---------------------------------------------------------------------------
# Async operations
# ---------------------------------------------------------------------------

class TestAsyncGeneration:
    """Tests for async drawing generation."""

    @pytest.mark.asyncio
    async def test_async_generate(self, generator: DrawingNumberGenerator) -> None:
        result = await generator.async_generate(Discipline.ELECTRICAL)
        assert result.drawing_number.formatted == "MS-E-0001-A"

    @pytest.mark.asyncio
    async def test_async_batch(self, generator: DrawingNumberGenerator) -> None:
        results: list[GenerationResult] = []
        async for result in generator.async_generate_batch(Discipline.MECHANICAL, 5):
            results.append(result)
        assert len(results) == 5
        sequences = [r.drawing_number.sequence for r in results]
        assert sequences == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_async_concurrent_safety(
        self, generator: DrawingNumberGenerator
    ) -> None:
        """Concurrent async calls must not produce duplicate sequences."""
        tasks = [
            generator.async_generate(Discipline.STRUCTURAL)
            for _ in range(10)
        ]
        results = await asyncio.gather(*tasks)
        sequences = sorted(r.drawing_number.sequence for r in results)
        assert sequences == list(range(1, 11))


# ---------------------------------------------------------------------------
# Bulk generation
# ---------------------------------------------------------------------------

class TestBulkGeneration:
    """Tests for synchronous bulk generation."""

    def test_bulk_generate(self, generator: DrawingNumberGenerator) -> None:
        results = generator.bulk_generate(Discipline.OPTICAL, 3)
        assert len(results) == 3
        assert results[0].drawing_number.sequence == 1
        assert results[2].drawing_number.sequence == 3

    def test_bulk_zero_count_rejected(
        self, generator: DrawingNumberGenerator
    ) -> None:
        with pytest.raises(ValueError, match="positive"):
            generator.bulk_generate(Discipline.OPTICAL, 0)


# ---------------------------------------------------------------------------
# Configuration loading
# ---------------------------------------------------------------------------

class TestConfigLoading:
    """Tests for configuration loading from env vars."""

    def test_env_var_override(self) -> None:
        with patch.dict(os.environ, {"EPDM_PROJECT_PREFIX": "TST"}):
            config = load_config(overrides={})
            assert config.project_prefix == "TST"

    def test_explicit_override_wins(self) -> None:
        with patch.dict(os.environ, {"EPDM_PROJECT_PREFIX": "ENV"}):
            config = load_config(overrides={"project_prefix": "OVR"})
            assert config.project_prefix == "OVR"


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

class TestLookup:
    """Tests for registry lookup."""

    def test_lookup_existing(self, generator: DrawingNumberGenerator) -> None:
        generator.generate(Discipline.ELECTRICAL)
        result = generator.lookup("MS-E-0001-A")
        assert result is not None
        assert result.formatted == "MS-E-0001-A"

    def test_lookup_missing(self, generator: DrawingNumberGenerator) -> None:
        assert generator.lookup("MS-E-9999-A") is None
