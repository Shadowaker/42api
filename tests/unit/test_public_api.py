def test_top_level_exports_are_importable() -> None:
    from intra42 import (
        Accreditation,
        AsyncClient,
        AuthenticationError,
        Campus,
        CampusUser,
        Client,
        ClientConfig,
        Cursus,
        Event,
        FortyTwoAPIError,
        Location,
        NetworkError,
        NotFoundError,
        PermissionDeniedError,
        Project,
        ProjectUser,
        RateLimitError,
        ServerError,
        User,
        ValidationError,
    )

    assert AsyncClient is not None
    assert Client is not None
    assert ClientConfig is not None
    assert Accreditation is not None
    assert User is not None
    assert Campus is not None
    assert CampusUser is not None
    assert Cursus is not None
    assert Event is not None
    assert Location is not None
    assert Project is not None
    assert ProjectUser is not None
    assert issubclass(AuthenticationError, FortyTwoAPIError)
    assert issubclass(NetworkError, FortyTwoAPIError)
    assert issubclass(NotFoundError, FortyTwoAPIError)
    assert issubclass(PermissionDeniedError, FortyTwoAPIError)
    assert issubclass(RateLimitError, FortyTwoAPIError)
    assert issubclass(ServerError, FortyTwoAPIError)
    assert issubclass(ValidationError, FortyTwoAPIError)
