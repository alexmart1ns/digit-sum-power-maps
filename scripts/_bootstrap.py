"""Make ``dspm`` importable when running scripts from a source checkout.

Installing the package (``pip install -e .``) makes this unnecessary, but the
scripts should also work in a bare clone with no install step.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
