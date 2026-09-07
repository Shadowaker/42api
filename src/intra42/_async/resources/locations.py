from __future__ import annotations

from ...models.location import Location
from .base import AsyncResource


class AsyncLocationsResource(AsyncResource[Location]):
    path = "/locations"
    model = Location

    async def graph(
        self, *, field: str | None = None, interval: str | None = None
    ) -> dict[str, int]:
        """Grouped temporal counts (``GET /locations/graph...``).

        Not a paginated list of ``Location`` objects — returns a raw
        ``{date_string: count}`` mapping, counting occurrences of `field`
        (default ``begin_at``) bucketed by `interval` (default
        ``month_of_year``) from the first occurrence to now.
        """

        path = "/locations/graph"
        if interval is not None and field is None:
            field = "begin_at"
        if field is not None:
            path += f"/on/{field}"
            if interval is not None:
                path += f"/by/{interval}"
        response = await self._client.request("GET", path)
        return response.json()
