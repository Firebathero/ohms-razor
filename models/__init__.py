"""Models 1-5 from the handoff, as pure functions. No I/O anywhere in this package;
loading data and rendering tables live in scripts/. Every function states its formula
so a reader can check the arithmetic without leaving the docstring.
"""

SECONDS_PER_YEAR = 31_557_600.0  # 365.25 * 86400
HOURS_PER_YEAR = 8766.0  # 365.25 * 24
MTOK = 1e6
