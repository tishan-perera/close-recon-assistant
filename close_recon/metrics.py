"""Counts from one close. The README quotes only what this module returns."""

from __future__ import annotations

import json
from collections import Counter

from close_recon.audit import posted_count
from close_recon.models import CloseResult
from close_recon.money import plain


def classified_ids(result: CloseResult, side: str) -> list[str]:
    """Line ids that landed in one primary bucket.

    A line is classified when it is in a match or suggestion, held as a
    duplicate, or placed in a timing or bank-only reconciling bucket.
    """
    lines = result.books.bank if side == "bank" else result.books.gl
    ids = {line.line_id for line in lines}
    found: list[str] = []
    for link in result.match.links:
        found.extend(link.bank_ids if side == "bank" else link.gl_ids)
    for flag in result.match.duplicates:
        if flag.side == side:
            found.append(flag.line_id)
    if side == "bank":
        kinds = {"unrecorded_interest", "unrecorded_bank_charge", "unrecorded_bank_amount"}
    else:
        kinds = {"deposit_in_transit", "outstanding_payment"}
    for item in result.reconciliation.items:
        if item.kind in kinds:
            found.extend(source for source in item.source_ids if source in ids)
    return found


def sample_counts(result: CloseResult) -> dict[str, object]:
    """Stable counts for the synthetic month. No rates are invented here."""
    rules = Counter(link.rule for link in result.match.links)
    bank_classified = classified_ids(result, "bank")
    gl_classified = classified_ids(result, "book")
    return {
        "data_origin": result.books.period.data_origin,
        "entity_name": result.books.period.entity_name,
        "period": result.books.period.period,
        "bank_lines": len(result.books.bank),
        "gl_lines": len(result.books.gl),
        "expense_lines": len(result.books.expenses),
        "bank_lines_classified": len(bank_classified),
        "gl_lines_classified": len(gl_classified),
        "matched_groups": sum(1 for link in result.match.links if link.status == "matched"),
        "suggested_groups": sum(1 for link in result.match.links if link.status == "suggested"),
        "duplicate_flags": len(result.match.duplicates),
        "ambiguities": len(result.match.ambiguities),
        "reconciling_items": len(result.reconciliation.items),
        "review_pending": sum(1 for item in result.review if item.status == "pending"),
        "categories_flagged_for_review": sum(1 for item in result.categories if item.needs_review),
        "category_source_rules": sum(1 for item in result.categories if item.source == "rules"),
        "category_source_llm": sum(1 for item in result.categories if item.source == "llm"),
        "journal_entries_posted": posted_count(result.categories),
        "llm_enabled": result.llm_enabled,
        "unexplained_difference": plain(result.reconciliation.unexplained),
        "bank_balance": plain(result.reconciliation.bank_balance),
        "book_balance": plain(result.reconciliation.book_balance),
        "adjusted_bank": plain(result.reconciliation.adjusted_bank),
        "adjusted_book": plain(result.reconciliation.adjusted_book),
        "match_rule_counts": dict(sorted(rules.items())),
        "audit_events": len(result.audit),
    }


def main() -> int:
    from pathlib import Path

    from close_recon.pipeline import run_close

    root = Path(__file__).resolve().parents[1]
    result = run_close(root / "sample-data", as_of="2026-04-02T15:00:00+00:00")
    print(json.dumps(sample_counts(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
