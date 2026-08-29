"""Puts the repo root on sys.path so tests can import models/ and scripts/."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for p in (ROOT, ROOT / "scripts"):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
