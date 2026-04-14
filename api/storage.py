"""In-memory drawing store seeded with realistic fixture data.

Wraps the core DrawingNumberGenerator and adds presentation metadata
(drawing type, creation timestamp, title) needed by the web UI.
"""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, Field

from drawing_generator.generator import DrawingNumberGenerator
from drawing_generator.models import Discipline, DrawingConfig, DrawingNumber


DRAWING_TYPES: list[str] = [
    "Assembly",
    "Detail",
    "Schematic",
    "Layout",
    "Wiring",
    "Foundation",
    "PV Array",
    "Tracker",
]


class Drawing(BaseModel):
    """Web-facing drawing record, extends DrawingNumber with UI metadata."""

    id: str = Field(..., description="Formatted drawing number, primary key")
    prefix: str
    discipline: Discipline
    discipline_name: str
    sequence: int
    revision: str
    drawing_type: str
    title: str
    vault_path: str
    created_at: datetime
    is_new: bool = True

    @classmethod
    def from_number(
        cls,
        dn: DrawingNumber,
        drawing_type: str,
        title: str,
        vault_path: str,
        created_at: datetime,
        is_new: bool = True,
    ) -> "Drawing":
        return cls(
            id=dn.formatted,
            prefix=dn.prefix,
            discipline=dn.discipline,
            discipline_name=dn.discipline.name,
            sequence=dn.sequence,
            revision=dn.revision,
            drawing_type=drawing_type,
            title=title,
            vault_path=vault_path,
            created_at=created_at,
            is_new=is_new,
        )


class DrawingStore:
    """Thread-safe singleton-style store wrapping the generator."""

    def __init__(self) -> None:
        self._config = DrawingConfig(project_prefix="MS")
        self._generator = DrawingNumberGenerator(self._config)
        self._drawings: dict[str, Drawing] = {}
        self._lock = threading.Lock()
        self._seed()

    def _seed(self) -> None:
        """Populate the store with realistic fixture drawings."""
        base_time = datetime.now(timezone.utc) - timedelta(days=45)
        fixtures: list[tuple[str, Discipline, str, str]] = [
            ("MS", Discipline.ELECTRICAL, "Combiner Box", "Wiring"),
            ("MS", Discipline.ELECTRICAL, "DC Home Run", "Schematic"),
            ("MS", Discipline.ELECTRICAL, "Inverter Pad", "Layout"),
            ("MS", Discipline.MECHANICAL, "Tracker Drive Assembly", "Assembly"),
            ("MS", Discipline.MECHANICAL, "Torque Tube Joint", "Detail"),
            ("MS", Discipline.MECHANICAL, "Damper Bracket", "Detail"),
            ("MS", Discipline.STRUCTURAL, "Pile Foundation", "Foundation"),
            ("MS", Discipline.STRUCTURAL, "Wind Load Bracing", "Detail"),
            ("MS", Discipline.STRUCTURAL, "Array Layout Plan", "Layout"),
            ("MS", Discipline.OPTICAL, "Concentrator Lens", "Detail"),
            ("MS", Discipline.OPTICAL, "Secondary Optic", "Assembly"),
            ("MS", Discipline.OPTICAL, "Light Guide", "Schematic"),
            ("MS", Discipline.ELECTRICAL, "AC Collection", "Wiring"),
            ("MS", Discipline.STRUCTURAL, "Tracker Row Frame", "Assembly"),
            ("MS", Discipline.MECHANICAL, "Bearing Housing", "Detail"),
            ("MS", Discipline.OPTICAL, "Receiver Module", "PV Array"),
            ("MS", Discipline.MECHANICAL, "Drive Coupling", "Assembly"),
            ("MS", Discipline.ELECTRICAL, "Tracker Motor Control", "Schematic"),
        ]

        for idx, (prefix, disc, title, dtype) in enumerate(fixtures):
            result = self._generator.generate(disc)
            created = base_time + timedelta(days=idx * 2, hours=idx)
            drawing = Drawing.from_number(
                dn=result.drawing_number,
                drawing_type=dtype,
                title=title,
                vault_path=result.vault_path,
                created_at=created,
                is_new=True,
            )
            self._drawings[drawing.id] = drawing

    def list_all(
        self,
        page: int = 1,
        size: int = 50,
        sort_by: str = "created_at",
        descending: bool = True,
        discipline: Optional[Discipline] = None,
        search: Optional[str] = None,
    ) -> tuple[list[Drawing], int]:
        """Return a paginated, filtered, sorted drawing list.

        Returns (items, total_count).
        """
        with self._lock:
            items = list(self._drawings.values())

        if discipline is not None:
            items = [d for d in items if d.discipline == discipline]

        if search:
            q = search.strip().lower()
            items = [
                d for d in items
                if q in d.id.lower()
                or q in d.title.lower()
                or q in d.drawing_type.lower()
            ]

        key_fn = {
            "created_at": lambda d: d.created_at,
            "id": lambda d: d.id,
            "discipline": lambda d: d.discipline.value,
            "sequence": lambda d: d.sequence,
            "revision": lambda d: d.revision,
            "drawing_type": lambda d: d.drawing_type,
        }.get(sort_by, lambda d: d.created_at)

        items.sort(key=key_fn, reverse=descending)

        total = len(items)
        start = max(0, (page - 1) * size)
        end = start + size
        return items[start:end], total

    def get(self, drawing_id: str) -> Optional[Drawing]:
        with self._lock:
            return self._drawings.get(drawing_id.strip().upper())

    def generate(
        self,
        project_code: str,
        discipline: Discipline,
        revision: str,
        drawing_type: str,
        title: Optional[str] = None,
    ) -> Drawing:
        """Generate a new drawing using the core engine."""
        with self._lock:
            if project_code.upper() != self._config.project_prefix:
                self._config = DrawingConfig(
                    project_prefix=project_code,
                    default_revision=revision,
                )
                self._generator = DrawingNumberGenerator(self._config)
                for existing_id in self._drawings:
                    try:
                        parsed = DrawingNumber.parse(existing_id)
                        self._generator._registry[parsed.formatted] = parsed
                        current = self._generator._sequences[parsed.discipline]
                        if parsed.sequence > current:
                            self._generator._sequences[parsed.discipline] = parsed.sequence
                    except ValueError:
                        continue

            result = self._generator.generate(discipline)
            dn = result.drawing_number
            if dn.revision != revision:
                dn = dn.model_copy(update={"revision": revision})
                self._generator._registry.pop(result.drawing_number.formatted, None)
                self._generator._registry[dn.formatted] = dn

            resolved_title = title or f"{drawing_type} - {discipline.name.title()}"
            drawing = Drawing.from_number(
                dn=dn,
                drawing_type=drawing_type,
                title=resolved_title,
                vault_path=result.vault_path.replace(
                    result.drawing_number.formatted, dn.formatted
                ),
                created_at=datetime.now(timezone.utc),
                is_new=True,
            )
            self._drawings[drawing.id] = drawing
            return drawing


_store: Optional[DrawingStore] = None


def get_store() -> DrawingStore:
    """Return the process-wide store, building it on first call."""
    global _store
    if _store is None:
        _store = DrawingStore()
    return _store
