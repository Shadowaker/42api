from intra42._pagination import parse_link_header


def test_none_returns_empty() -> None:
    assert parse_link_header(None) == {}


def test_empty_string_returns_empty() -> None:
    assert parse_link_header("") == {}


def test_single_rel() -> None:
    header = '<https://api.intra.42.fr/v2/users?page=2>; rel="next"'
    assert parse_link_header(header) == {"next": "https://api.intra.42.fr/v2/users?page=2"}


def test_multiple_rels() -> None:
    header = (
        '<https://api.intra.42.fr/v2/users?page=2>; rel="next", '
        '<https://api.intra.42.fr/v2/users?page=42>; rel="last"'
    )
    assert parse_link_header(header) == {
        "next": "https://api.intra.42.fr/v2/users?page=2",
        "last": "https://api.intra.42.fr/v2/users?page=42",
    }
