"""Drawing number generation module for EPDM systems.

Provides typed, validated, async-capable drawing number generation
following the format: {PREFIX}-{DISCIPLINE}-{SEQ:04d}-{REV}
"""

from drawing_generator.models import (
    Discipline,
    DrawingConfig,
    DrawingNumber,
    GenerationResult,
)
from drawing_generator.generator import DrawingNumberGenerator

__all__ = [
    "Discipline",
    "DrawingConfig",
    "DrawingNumber",
    "DrawingNumberGenerator",
    "GenerationResult",
]

__version__ = "1.0.0"
