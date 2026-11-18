#!/usr/bin/env python3
"""Print the synthetic-month counts cited in the README.

The numbers come from one offline run of the sample books. This script does
not call a model and does not score a hidden gold set.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from close_recon.metrics import main

if __name__ == "__main__":
    raise SystemExit(main())
