"""Command line for the sample close. The model flag cannot reach the network."""

from __future__ import annotations

import sys
from pathlib import Path

from close_recon.load import DataError
from close_recon.models import CloseReconError, LlmNotConfigured
from close_recon.pipeline import run_close
from close_recon.report import format_summary
from close_recon.review import ReviewError, load_decisions


def project_root() -> Path:
    """Repository root when the command is run from a checkout.

    An installed copy falls back to the directory that contains this package.
    Sample files are not shipped inside the wheel; run the command from the
    repository so ``sample-data/`` is found.
    """
    cwd = Path.cwd()
    if (cwd / "sample-data" / "period.json").is_file():
        return cwd
    return Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    import argparse

    root = project_root()
    parser = argparse.ArgumentParser(
        prog="close_recon",
        description="Reconcile a synthetic cash account and draft a month-end checklist.",
    )
    parser.add_argument("--data", type=Path, default=root / "sample-data")
    parser.add_argument("--output", type=Path, default=root / "output")
    parser.add_argument("--as-of", default="2026-04-02T15:00:00+00:00")
    parser.add_argument("--decisions", type=Path, default=None)
    parser.add_argument(
        "--enable-llm",
        action="store_true",
        help="Refused by this CLI. Tests inject an in-process suggester instead.",
    )
    args = parser.parse_args(argv)
    if args.enable_llm:
        print(
            "The LLM step has no network client. This CLI will not enable it. "
            "Call run_close from Python and pass an in-process suggester.",
            file=sys.stderr,
        )
        return 2
    try:
        decisions = load_decisions(args.decisions) if args.decisions else None
        result = run_close(
            data_dir=args.data,
            output_dir=args.output,
            as_of=args.as_of,
            decisions=decisions,
        )
    except (CloseReconError, LlmNotConfigured, ReviewError, DataError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    sys.stdout.write(format_summary(result))
    print(f"Outputs: {_display_path(args.output)}")
    return 0


def _display_path(path: Path) -> Path:
    """Prefer a path relative to the working directory when the run wrote there."""
    try:
        return path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        return path
