from intra42._query_params import build_query_params


def test_no_args_returns_empty_dict() -> None:
    assert build_query_params() == {}


def test_single_filter() -> None:
    assert build_query_params(filters={"campus_id": 1}) == {"filter[campus_id]": "1"}


def test_list_filter_is_comma_joined() -> None:
    assert build_query_params(filters={"campus_id": [1, 2, 3]}) == {"filter[campus_id]": "1,2,3"}


def test_bool_filter_lowercased() -> None:
    assert build_query_params(filters={"active": True}) == {"filter[active]": "true"}


def test_sort_joins_multiple_fields() -> None:
    assert build_query_params(sort=["-level", "login"]) == {"sort": "-level,login"}


def test_page_size_and_number() -> None:
    assert build_query_params(page_size=30, page_number=2) == {
        "page[size]": "30",
        "page[number]": "2",
    }


def test_range() -> None:
    assert build_query_params(ranges={"id": (1, 100)}) == {"range[id]": "1,100"}


def test_all_combined() -> None:
    params = build_query_params(
        filters={"campus_id": 1},
        sort=["-level"],
        page_size=10,
        ranges={"id": (1, 50)},
    )
    assert params == {
        "filter[campus_id]": "1",
        "sort": "-level",
        "page[size]": "10",
        "range[id]": "1,50",
    }
