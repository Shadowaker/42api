"""Pure helper for safely interpolating caller-supplied values into URL paths."""

from __future__ import annotations

from urllib.parse import quote


def path_segment(value: int | str) -> str:
    """Encode ``value`` as a single URL path segment.

    Percent-encodes everything outside the unreserved set, including ``/``,
    ``?`` and ``#``, so a value like ``"../campus/1"`` can't escape its
    segment and hit a different endpoint.
    """
    text = str(value)
    if text in ("", ".", ".."):
        raise ValueError(f"Invalid path segment: {text!r}")
    return quote(text, safe="")
