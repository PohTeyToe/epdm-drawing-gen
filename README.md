# EPDM Drawing Number Generator — Modern Python Backend Modernization Demo

Demonstrates transforming a legacy engineering script into a production-ready Python module with type safety, validation, async support, and comprehensive testing.

## Before vs After

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

## Features

- **Pydantic v2 models** — `DrawingNumber`, `DrawingConfig`, and `GenerationResult` with field validators, model validators, and strict constraints
- **Async support** — `async_generate()` and `async_generate_batch()` use `asyncio.Lock` for safe concurrent access, ready for real EPDM vault API integration
- **Custom exception hierarchy** — `SequenceExhaustedError`, `DuplicateDrawingError`, `RevisionError` give callers precise failure modes to handle
- **42 pytest cases** — covering generation, sequencing, revisions, parsing, model validation, discipline resolution, async concurrency, bulk operations, config loading, and registry lookup
- **CLI interface** — `generate`, `revise`, and `parse` subcommands via `argparse`
- **Layered configuration** — explicit overrides > environment variables > YAML file > defaults

## Tech Stack

- Python 3.11+
- Pydantic v2
- pytest + pytest-asyncio
- asyncio

## Quick Start

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

## Test Results

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

## Drawing Number Format

```
{PREFIX}-{DISCIPLINE}-{SEQ:04d}-{REV}
```

- **PREFIX**: 2-4 character project code (e.g., `MS`)
- **DISCIPLINE**: `E` (Electrical), `M` (Mechanical), `S` (Structural), `O` (Optical)
- **SEQ**: Auto-incrementing 4-digit sequence per discipline
- **REV**: Revision letter (`A` through `Z`)

Examples: `MS-E-0001-A`, `MS-O-0042-B`

## Project Structure

```
morgan-solar-drawing-gen/
├── drawing_generator/
│   ├── __init__.py          # Public API exports
│   ├── config.py            # Layered configuration loading (YAML / env / overrides)
│   ├── generator.py         # Core generation engine + custom exceptions
│   └── models.py            # Pydantic v2 models (DrawingNumber, DrawingConfig, GenerationResult)
├── tests/
│   ├── __init__.py
│   └── test_generator.py    # 42-case pytest suite
├── legacy_example.py        # The "before" — messy legacy script
├── main.py                  # CLI entry point (generate / revise / parse)
├── pyproject.toml           # Modern Python packaging + tool config
└── README.md
```

## Configuration

Configuration loads with the following priority (highest wins):

1. Explicit overrides (CLI arguments)
2. Environment variables (`EPDM_PROJECT_PREFIX`, `EPDM_HOST`, `EPDM_VAULT`, etc.)
3. YAML config file
4. Defaults

---

Built as a proof-of-concept for Morgan Solar's EPDM Backend Modernization project (Advance Ontario, April 2026).
