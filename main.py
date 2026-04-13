"""CLI entry point for the drawing number generator.

Usage:
    python main.py generate --discipline E --project MS
    python main.py generate --discipline MECHANICAL --project MS --count 5
    python main.py revise --drawing MS-E-0001-A --project MS
    python main.py parse MS-O-0042-B
"""

from __future__ import annotations

import argparse
import sys

from drawing_generator.config import load_config
from drawing_generator.generator import DrawingNumberError, DrawingNumberGenerator
from drawing_generator.models import Discipline


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and dispatch to the appropriate command."""
    parser = argparse.ArgumentParser(
        description="Engineering drawing number generator (EPDM modernization demo)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- generate ---
    gen_parser = subparsers.add_parser("generate", help="Generate new drawing numbers")
    gen_parser.add_argument(
        "--discipline", "-d",
        required=True,
        help="Discipline code or name: E, M, S, O (or full name)",
    )
    gen_parser.add_argument(
        "--project", "-p",
        default="MS",
        help="Project prefix (default: MS)",
    )
    gen_parser.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        help="Number of drawing numbers to generate (default: 1)",
    )

    # --- revise ---
    rev_parser = subparsers.add_parser("revise", help="Revise an existing drawing")
    rev_parser.add_argument("--drawing", required=True, help="Drawing number to revise")
    rev_parser.add_argument("--project", "-p", default="MS", help="Project prefix")

    # --- parse ---
    parse_parser = subparsers.add_parser("parse", help="Parse a drawing number string")
    parse_parser.add_argument("drawing_number", help="Drawing number to parse")

    args = parser.parse_args(argv)

    try:
        if args.command == "generate":
            return _handle_generate(args)
        elif args.command == "revise":
            return _handle_revise(args)
        elif args.command == "parse":
            return _handle_parse(args)
    except DrawingNumberError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 1

    return 0


def _handle_generate(args: argparse.Namespace) -> int:
    """Handle the 'generate' subcommand."""
    discipline = Discipline.from_string(args.discipline)
    config = load_config(overrides={"project_prefix": args.project})
    generator = DrawingNumberGenerator(config)

    results = generator.bulk_generate(discipline, args.count)

    print(f"Generated {len(results)} drawing number(s):\n")
    for result in results:
        print(f"  {result.drawing_number.formatted}")
        print(f"    Vault: {result.vault_path}")
        print()

    return 0


def _handle_revise(args: argparse.Namespace) -> int:
    """Handle the 'revise' subcommand.

    Note: In a real EPDM integration, the generator would load
    existing drawings from the vault. This demo pre-registers
    the drawing to simulate that workflow.
    """
    from drawing_generator.models import DrawingNumber as DN

    config = load_config(overrides={"project_prefix": args.project})
    generator = DrawingNumberGenerator(config)

    # Simulate loading existing drawing from EPDM vault
    existing = DN.parse(args.drawing)
    generator._registry[existing.formatted] = existing

    result = generator.revise(args.drawing)

    print(f"Revised drawing:\n")
    print(f"  Previous: {result.previous}")
    print(f"  New:      {result.drawing_number.formatted}")
    print(f"  Vault:    {result.vault_path}")

    return 0


def _handle_parse(args: argparse.Namespace) -> int:
    """Handle the 'parse' subcommand."""
    from drawing_generator.models import DrawingNumber

    dn = DrawingNumber.parse(args.drawing_number)

    print(f"Parsed drawing number: {dn.formatted}\n")
    print(f"  Prefix:     {dn.prefix}")
    print(f"  Discipline: {dn.discipline.name} ({dn.discipline.value})")
    print(f"  Sequence:   {dn.sequence}")
    print(f"  Revision:   {dn.revision}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
