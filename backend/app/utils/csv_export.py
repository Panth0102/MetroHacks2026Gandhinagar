"""Safe CSV serialization: quotes fields and neutralizes spreadsheet formula
injection (leading = + - @, tab, CR) by prefixing a single quote."""
from __future__ import annotations

import csv
import io
from collections.abc import Iterable, Sequence

_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _sanitize(value: object) -> str:
    s = "" if value is None else str(value)
    if s and s[0] in _FORMULA_PREFIXES:
        return "'" + s
    return s


def to_csv(headers: Sequence[str], rows: Iterable[Sequence[object]], preamble: list[str] | None = None) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    if preamble:
        for line in preamble:
            writer.writerow([_sanitize(line)])
    writer.writerow([_sanitize(h) for h in headers])
    for row in rows:
        writer.writerow([_sanitize(cell) for cell in row])
    return buf.getvalue()
