"""HTTP routes for the drawing registry."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from drawing_generator.models import Discipline

from api.storage import DRAWING_TYPES, Drawing, get_store


router = APIRouter()


class DrawingListResponse(BaseModel):
    items: list[Drawing]
    total: int
    page: int
    size: int


class GenerateRequest(BaseModel):
    project_code: str = Field(..., min_length=2, max_length=4)
    discipline: Discipline
    revision: str = Field("A", pattern=r"^[A-Z]$")
    drawing_type: str
    title: Optional[str] = None


class DisciplineOption(BaseModel):
    code: str
    name: str


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/disciplines", response_model=list[DisciplineOption])
def list_disciplines() -> list[DisciplineOption]:
    return [DisciplineOption(code=d.value, name=d.name.title()) for d in Discipline]


@router.get("/drawing-types", response_model=list[str])
def list_drawing_types() -> list[str]:
    return DRAWING_TYPES


@router.get("/drawings", response_model=DrawingListResponse)
def list_drawings(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    sort_by: str = Query("created_at"),
    descending: bool = Query(True),
    discipline: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
) -> DrawingListResponse:
    store = get_store()
    disc: Optional[Discipline] = None
    if discipline:
        try:
            disc = Discipline.from_string(discipline)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    items, total = store.list_all(
        page=page,
        size=size,
        sort_by=sort_by,
        descending=descending,
        discipline=disc,
        search=search,
    )
    return DrawingListResponse(items=items, total=total, page=page, size=size)


@router.get("/drawings/{drawing_id}", response_model=Drawing)
def get_drawing(drawing_id: str) -> Drawing:
    store = get_store()
    drawing = store.get(drawing_id)
    if drawing is None:
        raise HTTPException(status_code=404, detail=f"Drawing '{drawing_id}' not found")
    return drawing


@router.post("/drawings/generate", response_model=Drawing, status_code=201)
def generate_drawing(payload: GenerateRequest) -> Drawing:
    store = get_store()
    try:
        return store.generate(
            project_code=payload.project_code.upper(),
            discipline=payload.discipline,
            revision=payload.revision.upper(),
            drawing_type=payload.drawing_type,
            title=payload.title,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
