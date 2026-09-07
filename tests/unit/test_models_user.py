from intra42.models.user import User


def test_minimal_user_parses() -> None:
    user = User.model_validate({"id": 1, "login": "jdoe"})
    assert user.id == 1
    assert user.login == "jdoe"


def test_unknown_field_is_tolerated_and_kept_in_extra() -> None:
    user = User.model_validate({"id": 1, "login": "jdoe", "some_future_field": "x"})
    assert user.model_extra is not None
    assert user.model_extra["some_future_field"] == "x"


def test_staff_question_mark_field_aliased() -> None:
    user = User.model_validate({"id": 1, "staff?": True})
    assert user.staff is True


def test_nested_image_parses() -> None:
    user = User.model_validate(
        {
            "id": 1,
            "login": "jdoe",
            "image": {
                "link": "https://example.com/a.jpg",
                "versions": {"large": "https://example.com/a_l.jpg"},
            },
        }
    )
    assert user.image is not None
    assert user.image.versions is not None
    assert user.image.versions.large == "https://example.com/a_l.jpg"


def test_alumni_and_active_question_mark_fields_aliased() -> None:
    user = User.model_validate({"id": 1, "alumni?": True, "active?": False})
    assert user.alumni is True
    assert user.active is False
