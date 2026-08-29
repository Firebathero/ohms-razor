"""Prints the repo's current answer to the two modern questions, solved from data/:

    what do I use for compute?   (deterministic work)
    what do I use for tokens?    (thinking)

Same content as the README's answer block; this is the terminal form. If the output here
disagrees with the README, run build_tables.py, because one of them is stale and it is
never this one.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_tables  # noqa: E402


def main() -> int:
    print("\n".join(build_tables.placement_lines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
