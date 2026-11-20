import pytest

from intra42._paths import path_segment


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (42, "42"),
        ("jdoe", "jdoe"),
        ("j.doe-_~", "j.doe-_~"),  # unreserved chars pass through
        ("../campus/1", "..%2Fcampus%2F1"),
        ("a?b#c", "a%3Fb%23c"),
        ("a b", "a%20b"),
        ("%2F", "%252F"),  # already-encoded input is encoded again, not trusted
    ],
)
def test_path_segment_encodes(value: int | str, expected: str) -> None:
    assert path_segment(value) == expected


@pytest.mark.parametrize("value", ["", ".", ".."])
def test_path_segment_rejects_dot_and_empty_segments(value: str) -> None:
    with pytest.raises(ValueError, match="Invalid path segment"):
        path_segment(value)
