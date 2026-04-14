# EPDM Drawing Number Generator — Modern Python Backend Modernization Demo

Demonstrates transforming a legacy engineering script into a production-ready Python module with type safety, validation, async support, and comprehensive testing. Ships with a FastAPI wrapper and a React web UI so reviewers can exercise the system without installing Python.

## Web UI

A React + FastAPI front-end sits on top of the core package. Engineering reviewers can browse, filter, and generate drawing numbers from the browser.

### Run locally

```bash
# Terminal 1 — backend (FastAPI on 8003)
pip install -r api/requirements.txt
uvicorn api.main:app --port 8003 --reload

# Terminal 2 — frontend (Vite on 5183)
cd frontend
npm install
npm run dev
```

Open http://localhost:5183. The frontend proxies `/api/*` to `http://localhost:8003` during dev.

### Stack

| Layer | Tech |
|-|-|
| Backend | FastAPI, Pydantic v2, uvicorn |
| Frontend | React 19, TypeScript, Vite, Tailwind v4, Framer Motion, @tanstack/react-table, lucide-react, react-hot-toast |
| Port | Backend `8003`, Frontend `5183` |

### Endpoints

| Method | Path | Purpose |
|-|-|-|
| GET | `/drawings` | Paginated list with `page`, `size`, `sort_by`, `descending`, `discipline`, `search` query params |
| GET | `/drawings/{id}` | Single drawing detail |
| POST | `/drawings/generate` | Generate a new drawing number |
| GET | `/disciplines` | Available engineering disciplines |
| GET | `/drawing-types` | Available drawing type options |
| GET | `/health` | Liveness check |

### Frontend features

- Hero header with grid-paper background and solar accent
- Sortable, filterable drawings table with discipline badges and monospace IDs
- Search + discipline dropdown + "Generate New" action
- Quick-generate modal, revision picker, type dropdown, toast on success
- Slide-in drawing detail drawer with SVG preview and bottom-right stamp box
- Graceful empty state when the API is unreachable

### Production build

```bash
cd frontend
npm run build        # outputs to frontend/dist
```

Set `VITE_API_URL` at build time to point the deployed frontend at a non-localhost backend. Leave it unset to use the dev proxy.

---

## CLI (original)

The original CLI remains intact for batch work and scripting.

### Before vs After

The `legacy_example.py` file captures the "before" state: a single-file script relying on global mutable counters, raw string concatenation, no type hints, no input validation, no error handling, and zero testability. Running it with an invalid discipline silently returns `None`. Revising past revision Z produces garbage. There is no way to test any of it without importing and mutating module-level state.

The modernized `drawing_generator/` package replaces all of that with encapsulated classes, Pydantic-validated models, a custom exception hierarchy, async-safe concurrency, layered configuration, and a full pytest suite.

| Before (`legacy_example.py`) | After (`drawing_generator/`) |
|-|-|
| Global mutable state | Encapsulated classes with clear ownership |
| No type hints | Full type annotations with generics |
| String concatenation | Pydantic models with field validation |
| No error handling | Custom exception hierarchy (`SequenceExhaustedError`, `DuplicateDrawingError`, `RevisionError`) |
| Untestable | 42 pytest cases with async coverage |
| No configuration | YAML/env-based config with layered overrides |
| Synchronous only | Async-ready with `asyncio.Lock` for concurrency |

### Features

- **Pydantic v2 models** — `DrawingNumber`, `DrawingConfig`, and `GenerationResult` with field validators, model validators, and strict constraints
- **Async support** — `async_generate()` and `async_generate_batch()` use `asyncio.Lock` for safe concurrent access, ready for real EPDM vault API integration
- **Custom exception hierarchy** — `SequenceExhaustedError`, `DuplicateDrawingError`, `RevisionError` give callers precise failure modes to handle
- **42 pytest cases** — covering generation, sequencing, revisions, parsing, model validation, discipline resolution, async concurrency, bulk operations, config loading, and registry lookup
- **CLI interface** — `generate`, `revise`, and `parse` subcommands via `argparse`
- **Layered configuration** — explicit overrides > environment variables > YAML file > defaults

### Tech Stack

- Python 3.11+
- Pydantic v2
- pytest + pytest-asyncio
- asyncio

### Quick Start

```bash
# Install dependencies
pip install pydantic pyyaml

# Generate a drawing number
python main.py generate --discipline E --project MS

# Generate multiple
python main.py generate --discipline MECHANICAL --project MS --count 5

# Parse a drawing number
python main.py parse MS-O-0042-B

# Revise an existing drawing
python main.py revise --drawing MS-E-0001-A --project MS

# Run tests
python -m pytest tests/ -v
```

### Test Results

**42/42 tests passing** across 10 test classes:

| Category | Tests | What's covered |
|-|-|-|
| Generation | 5 | All four disciplines + vault path format |
| Sequencing | 3 | Auto-increment, cross-discipline independence, exhaustion |
| Revisions | 4 | Single revision, chained revisions, Z-limit, missing drawing |
| Parsing | 11 | 4 valid format variations + 7 invalid format rejections (parametrized) |
| Model validation | 6 | Prefix constraints, case normalization, revision chain consistency |
| Discipline enum | 4 | Code lookup, name lookup, case insensitivity, unknown rejection |
| Async | 3 | Single generate, batch iterator, 10-way concurrent safety |
| Bulk generation | 2 | Multi-generate + zero-count rejection |
| Config loading | 2 | Env var override, explicit override precedence |
| Lookup | 2 | Registry hit + miss |

### Drawing Number Format

```
{PREFIX}-{DISCIPLINE}-{SEQ:04d}-{REV}
```

- **PREFIX**: 2-4 character project code (e.g., `MS`)
- **DISCIPLINE**: `E` (Electrical), `M` (Mechanical), `S` (Structural), `O` (Optical)
- **SEQ**: Auto-incrementing 4-digit sequence per discipline
- **REV**: Revision letter (`A` through `Z`)

Examples: `MS-E-0001-A`, `MS-O-0042-B`

### Project Structure

```
morgan-solar-drawing-gen/
├── api/                     # FastAPI web wrapper
│   ├── main.py              # App factory + CORS
│   ├── routes.py            # REST endpoints
│   ├── storage.py           # In-memory store seeded with fixtures
│   └── requirements.txt     # Web-only deps
├── frontend/                # React + Vite + Tailwind v4 UI
│   ├── src/
│   │   ├── components/      # Header, TopBar, DrawingsTable, GenerateModal, DrawingDrawer, EmptyState
│   │   ├── lib/             # api.ts, types.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── vite.config.ts
├── drawing_generator/
│   ├── __init__.py          # Public API exports
│   ├── config.py            # Layered configuration loading
│   ├── generator.py         # Core generation engine + custom exceptions
│   └── models.py            # Pydantic v2 models
├── tests/
│   ├── __init__.py
│   └── test_generator.py    # 42-case pytest suite
├── legacy_example.py        # The "before"
├── main.py                  # CLI entry point
├── pyproject.toml
└── README.md
```

### Configuration

Configuration loads with the following priority (highest wins):

1. Explicit overrides (CLI arguments)
2. Environment variables (`EPDM_PROJECT_PREFIX`, `EPDM_HOST`, `EPDM_VAULT`, etc.)
3. YAML config file
4. Defaults

---

Built as a proof-of-concept for Morgan Solar's EPDM Backend Modernization project (Advance Ontario, April 2026).
