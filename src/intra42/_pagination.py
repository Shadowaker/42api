"""Pure helper for parsing RFC 5988 ``Link`` headers.

42's API paginates list endpoints and advertises the next/first/last/prev
page URLs via a standard ``Link`` header: 
    <https://api.intra.42.fr/v2/users?page=2>; rel="next",
    <https://api.intra.42.fr/v2/users?page=42>; rel="last"
"""

from __future__ import annotations

import re

_LINK_RE = re.compile(r'<([^>]+)>\s*;\s*rel="([^"]+)"')


def parse_link_header(header_value: str | None) -> dict[str, str]:
    """Parse a ``Link`` header into a ``{rel: url}`` dict.

    Returns an empty dict for ``None`` or malformed input.
    """
    if not header_value:
        return {}
    return {rel: url for url, rel in _LINK_RE.findall(header_value)}
