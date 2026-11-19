"""The README may quote only the sample run, and it must say what this demo is."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from close_recon.pipeline import run_close
from close_recon.report import format_summary

AS_OF = "2026-04-02T15:00:00+00:00"
PITCH = "AI drafts the reconciliation. People approve the numbers."


class ReadmeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.metrics = json.loads(
            (ROOT / "eval" / "sample_metrics.json").read_text(encoding="utf-8")
        )

    def test_opening_states_the_pitch_the_notice_and_the_badges(self) -> None:
        self.assertIn(PITCH, self.readme)
        self.assertIn("synthetic demo data, not a product", self.readme.lower())
        self.assertIn("actions/workflows/ci.yml/badge.svg", self.readme)
        self.assertIn("license-MIT", self.readme)
        self.assertIn("python-3.11", self.readme)
        self.assertIn("docs/cli-run.png", self.readme)
        image = ROOT / "docs" / "cli-run.png"
        self.assertTrue(image.is_file(), "docs/cli-run.png is missing")
        self.assertEqual(image.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_readme_does_not_carry_private_project_material(self) -> None:
        lowered = self.readme.lower()
        for banned in ("grokbot", "robinhood", "proprietary license", "chat id"):
            self.assertNotIn(banned, lowered)

    def test_cli_block_is_the_engine_summary(self) -> None:
        summary = format_summary(run_close(ROOT / "sample-data", as_of=AS_OF)).strip()
        self.assertIn(summary, self.readme)

    def test_metric_tables_match_the_computed_file(self) -> None:
        metrics = self.metrics
        rows = {
            "Bank lines classified": f"{metrics['bank_lines_classified']} of {metrics['bank_lines']}",
            "Ledger lines classified": f"{metrics['gl_lines_classified']} of {metrics['gl_lines']}",
            "Expense lines": str(metrics["expense_lines"]),
            "Matched groups": str(metrics["matched_groups"]),
            "Suggested groups": str(metrics["suggested_groups"]),
            "Duplicate flags": str(metrics["duplicate_flags"]),
            "Ambiguous pairs left open": str(metrics["ambiguities"]),
            "Reconciling items": str(metrics["reconciling_items"]),
            "Review queue still pending": str(metrics["review_pending"]),
            "Categories flagged for review": str(metrics["categories_flagged_for_review"]),
            "Category drafts from rules": str(metrics["category_source_rules"]),
            "Category drafts from a model": str(metrics["category_source_llm"]),
            "Journal entries posted": str(metrics["journal_entries_posted"]),
            "Model step enabled": str(metrics["llm_enabled"]).lower(),
            "Unexplained difference (USD)": metrics["unexplained_difference"],
            "Bank balance (USD)": metrics["bank_balance"],
            "Book balance (USD)": metrics["book_balance"],
            "Adjusted bank (USD)": metrics["adjusted_bank"],
            "Adjusted book (USD)": metrics["adjusted_book"],
            "Audit events": str(metrics["audit_events"]),
        }
        for label, value in rows.items():
            self.assertIn(f"| {label} | {value} |", self.readme, label)
        for rule, count in metrics["match_rule_counts"].items():
            self.assertIn(f"| {rule} | {count} |", self.readme, rule)

    def test_flow_diagram_is_present(self) -> None:
        self.assertIn("```mermaid", self.readme)
        for phrase in (
            "Load GL cash and the bank statement",
            "Match",
            "Flag exceptions",
            "Draft explanations",
            "Person approves",
            "Logged",
        ):
            self.assertIn(phrase, self.readme)


if __name__ == "__main__":
    unittest.main()
