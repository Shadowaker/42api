from intra42.models.campus import Campus


def test_minimal_campus_parses() -> None:
    campus = Campus.model_validate({"id": 1, "name": "Paris"})
    assert campus.id == 1
    assert campus.name == "Paris"


def test_nested_language_parses() -> None:
    campus = Campus.model_validate(
        {"id": 1, "name": "Paris", "language": {"id": 1, "name": "Français", "identifier": "fr"}}
    )
    assert campus.language is not None
    assert campus.language.identifier == "fr"


def test_nested_endpoint_parses() -> None:
    campus = Campus.model_validate(
        {"id": 1, "name": "Paris", "endpoint": {"id": 5, "url": "https://example.com"}}
    )
    assert campus.endpoint is not None
    assert campus.endpoint.url == "https://example.com"
