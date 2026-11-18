"""The committed metrics file is the output of one offline sample run."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from close_recon.metrics import classified_ids, sample_counts
from close_recon.pipeline import run_close

AS_OF = "2026-04-02T15:00:00+00:00"


class MetricsTests(unittest.TestCase):
    def test_committed_file_matches_a_fresh_run(self) -> None:
        result = run_close(ROOT / "sample-data", as_of=AS_OF)
        fresh = sample_counts(result)
        committed = json.loads((ROOT / "eval" / "sample_metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, fresh)
        self.assertEqual(fresh["bank_lines_classified"], fresh["bank_lines"])
        self.assertEqual(fresh["gl_lines_classified"], fresh["gl_lines"])
        self.assertEqual(len(classified_ids(result, "bank")), fresh["bank_lines"])
        self.assertEqual(len(classified_ids(result, "book")), fresh["gl_lines"])
        self.assertEqual(fresh["journal_entries_posted"], 0)
        self.assertFalse(fresh["llm_enabled"])
        self.assertEqual(fresh["category_source_llm"], 0)
        self.assertEqual(fresh["data_origin"], "SYNTHETIC")


if __name__ == "__main__":
    unittest.main()
