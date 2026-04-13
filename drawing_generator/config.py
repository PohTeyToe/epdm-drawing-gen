"""Configuration management for EPDM drawing generation.

Loads configuration from YAML files or environment variables,
with sensible defaults for local development.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from drawing_generator.models import DrawingConfig

_ENV_PREFIX = "EPDM_"

_ENV_MAP: dict[str, str] = {
    "project_prefix": "PROJECT_PREFIX",
    "epdm_host": "HOST",
    "epdm_vault": "VAULT",
    "max_sequence": "MAX_SEQUENCE",
    "default_revision": "DEFAULT_REVISION",
}


def load_config(
    config_path: Optional[Path] = None,
    overrides: Optional[dict[str, object]] = None,
) -> DrawingConfig:
    """Load and merge configuration from file, env vars, and overrides.

    Priority (highest to lowest):
        1. Explicit overrides dict
        2. Environment variables (EPDM_PROJECT_PREFIX, EPDM_HOST, etc.)
        3. YAML config file
        4. Model defaults

    Args:
        config_path: Optional path to a YAML config file.
        overrides: Optional dict of field overrides.

    Returns:
        Validated DrawingConfig instance.
    """
    values: dict[str, object] = {}

    # Layer 1: YAML file
    if config_path and config_path.exists():
        values.update(_load_yaml(config_path))

    # Layer 2: Environment variables
    for field_name, env_suffix in _ENV_MAP.items():
        env_key = f"{_ENV_PREFIX}{env_suffix}"
        env_val = os.environ.get(env_key)
        if env_val is not None:
            values[field_name] = env_val

    # Layer 3: Explicit overrides
    if overrides:
        values.update(overrides)

    return DrawingConfig(**values)


def _load_yaml(path: Path) -> dict[str, object]:
    """Parse a YAML config file into a dict.

    Args:
        path: Path to the YAML file.

    Returns:
        Dict of configuration values.
    """
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        raise ImportError(
            "PyYAML is required to load YAML config files. "
            "Install it with: pip install pyyaml"
        )

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping in {path}, got {type(data).__name__}")

    return data
