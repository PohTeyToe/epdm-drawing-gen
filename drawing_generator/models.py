"""Pydantic models for drawing number generation and validation."""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Discipline(str, Enum):
    """Engineering discipline codes used in drawing numbers."""

    ELECTRICAL = "E"
    MECHANICAL = "M"
    STRUCTURAL = "S"
    OPTICAL = "O"

    @classmethod
    def from_string(cls, value: str) -> Discipline:
        """Resolve a discipline from its code or full name.

        Args:
            value: Single-letter code or full name (case-insensitive).

        Returns:
            Matching Discipline enum member.

        Raises:
            ValueError: If the value doesn't match any discipline.
        """
        normalized = value.strip().upper()
        # Try code match first
        for member in cls:
            if member.value == normalized:
                return member
        # Try name match
        for member in cls:
            if member.name == normalized:
                return member
        valid = ", ".join(f"{m.name} ({m.value})" for m in cls)
        raise ValueError(f"Unknown discipline '{value}'. Valid options: {valid}")


class DrawingConfig(BaseModel):
    """Configuration for the drawing number generator.

    Attributes:
        project_prefix: 2-4 character project code (e.g., "MS").
        epdm_host: Hostname of the EPDM vault server.
        epdm_vault: Name of the EPDM vault.
        max_sequence: Upper bound for sequence numbers per discipline.
        default_revision: Initial revision letter for new drawings.
    """

    project_prefix: str = Field(
        ...,
        min_length=2,
        max_length=4,
        description="Project code prefix for drawing numbers",
    )
    epdm_host: str = Field(
        default="localhost",
        description="EPDM vault server hostname",
    )
    epdm_vault: str = Field(
        default="ProductionVault",
        description="EPDM vault name",
    )
    max_sequence: int = Field(
        default=9999,
        ge=1,
        le=99999,
        description="Maximum sequence number per discipline",
    )
    default_revision: str = Field(
        default="A",
        pattern=r"^[A-Z]$",
        description="Initial revision letter",
    )

    @field_validator("project_prefix")
    @classmethod
    def validate_prefix(cls, v: str) -> str:
        """Ensure prefix contains only uppercase alphanumeric characters."""
        v = v.upper()
        if not re.match(r"^[A-Z0-9]{2,4}$", v):
            raise ValueError(
                f"Project prefix must be 2-4 alphanumeric characters, got '{v}'"
            )
        return v


class DrawingNumber(BaseModel):
    """A fully-qualified engineering drawing number.

    Attributes:
        prefix: Project code (e.g., "MS").
        discipline: Engineering discipline.
        sequence: Numeric sequence within the discipline.
        revision: Revision letter.
    """

    prefix: str
    discipline: Discipline
    sequence: int = Field(..., ge=1)
    revision: str = Field(..., pattern=r"^[A-Z]$")

    @property
    def formatted(self) -> str:
        """Render the canonical drawing number string."""
        return (
            f"{self.prefix}-{self.discipline.value}-"
            f"{self.sequence:04d}-{self.revision}"
        )

    @classmethod
    def parse(cls, drawing_number: str) -> DrawingNumber:
        """Parse a drawing number string into a structured object.

        Args:
            drawing_number: String like "MS-E-0001-A".

        Returns:
            Parsed DrawingNumber instance.

        Raises:
            ValueError: If the string doesn't match the expected format.
        """
        pattern = r"^([A-Z0-9]{2,4})-([EMSO])-(\d{4,5})-([A-Z])$"
        match = re.match(pattern, drawing_number.strip().upper())
        if not match:
            raise ValueError(
                f"Invalid drawing number format: '{drawing_number}'. "
                f"Expected format: PREFIX-DISCIPLINE-NNNN-R"
            )
        prefix, disc_code, seq_str, rev = match.groups()
        return cls(
            prefix=prefix,
            discipline=Discipline(disc_code),
            sequence=int(seq_str),
            revision=rev,
        )

    def next_revision(self) -> DrawingNumber:
        """Create a new DrawingNumber with the next revision letter.

        Returns:
            New DrawingNumber with incremented revision.

        Raises:
            ValueError: If the current revision is 'Z' (no further revisions).
        """
        if self.revision == "Z":
            raise ValueError(
                f"Drawing {self.formatted} is at revision Z; "
                f"cannot increment further"
            )
        next_rev = chr(ord(self.revision) + 1)
        return self.model_copy(update={"revision": next_rev})

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"DrawingNumber('{self.formatted}')"


class GenerationResult(BaseModel):
    """Result of a drawing number generation operation.

    Attributes:
        drawing_number: The generated drawing number.
        is_new: Whether this is a newly created number vs. a revision.
        previous: The prior drawing number if this is a revision.
        vault_path: Simulated EPDM vault path for the drawing.
    """

    drawing_number: DrawingNumber
    is_new: bool = True
    previous: Optional[DrawingNumber] = None
    vault_path: str = ""

    @model_validator(mode="after")
    def validate_revision_chain(self) -> GenerationResult:
        """Ensure revision metadata is consistent."""
        if not self.is_new and self.previous is None:
            raise ValueError(
                "Revised drawings must reference a previous drawing number"
            )
        if self.is_new and self.previous is not None:
            raise ValueError(
                "New drawings must not reference a previous drawing number"
            )
        return self

    def __str__(self) -> str:
        status = "NEW" if self.is_new else f"REV from {self.previous}"
        return f"[{status}] {self.drawing_number.formatted} -> {self.vault_path}"
