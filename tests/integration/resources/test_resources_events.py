import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client

EVENT_JSON = {
    "id": 3,
    "name": "Wyoming cattle",
    "description": "Accusantium lumbersexual pug minima.",
    "location": "Southern Bauch",
    "kind": "other",
    "max_people": 39,
    "nbr_subscribers": 0,
    "begin_at": "2017-11-24T13:42:10.014Z",
    "end_at": "2017-11-24T15:42:10.015Z",
    "campus_ids": [6],
    "cursus_ids": [1],
    "themes": [{"id": 36, "name": "AI", "created_at": None, "updated_at": None}],
    "waitlist": {
        "id": 391,
        "waitlistable_id": 3,
        "waitlistable_type": "Event",
        "created_at": None,
        "updated_at": None,
    },
    "prohibition_of_cancellation": 10,
    "created_at": "2017-11-22T13:42:10.037Z",
    "updated_at": "2017-11-22T13:42:10.082Z",
}


async def test_get_event_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/events/3").mock(
        return_value=httpx.Response(200, json=EVENT_JSON)
    )

    client = AsyncClient("id", "secret")
    try:
        event = await client.events.get(3)
    finally:
        await client.aclose()

    assert event.id == 3
    assert event.name == "Wyoming cattle"
    assert event.campus_ids == [6]
    assert event.themes is not None
    assert event.themes[0].name == "AI"
    assert event.waitlist is not None
    assert event.waitlist.waitlistable_type == "Event"


def test_get_event_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/events/3").mock(
        return_value=httpx.Response(200, json=EVENT_JSON)
    )

    with Client("id", "secret") as client:
        event = client.events.get(3)

    assert event.id == 3
    assert event.kind == "other"


async def test_event_with_null_waitlist_parses(mock_token_route) -> None:
    mock, _ = mock_token_route
    payload = dict(EVENT_JSON, id=4, waitlist=None)
    mock.get("https://api.intra.42.fr/v2/events/4").mock(
        return_value=httpx.Response(200, json=payload)
    )

    client = AsyncClient("id", "secret")
    try:
        event = await client.events.get(4)
    finally:
        await client.aclose()

    assert event.waitlist is None


async def test_filter_events_sends_query_params(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/events").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        await client.events.filter(future=True).sort("-begin_at").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[future]"] == "true"
    assert request.url.params["sort"] == "-begin_at"
