"""Remove project-specific labels from published dashboard text."""

from __future__ import annotations

import re

_REPLACEMENTS = (
    (re.compile(r"\bnative daily R06\b", re.I), "native daily frequency"),
    (re.compile(r"\bnative monthly R06\b", re.I), "native monthly frequency"),
    (re.compile(r"\bnative weekly R06\b", re.I), "native weekly frequency"),
    (re.compile(r"\bR06 sales\b", re.I), "pharmacy sales"),
    (re.compile(r"\bR06\b"), "target series"),
    (re.compile(r"\bRohto\b", re.I), "cosmetic pharma"),
    (re.compile(r"\(notebook 04\)", re.I), "(exogenous forecast pipeline)"),
    (re.compile(r"\bnotebook 98\b", re.I), "model comparison export"),
)


def sanitize_text(value: object) -> object:
    if not isinstance(value, str):
        return value
    text = value
    for pattern, replacement in _REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text.strip()
