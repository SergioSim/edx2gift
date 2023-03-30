"""Tests for edx2gift api."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials
from httpx import AsyncClient

from edx2gift.api import app, get_auth_username


def test_api_get_auth_username(monkeypatch):
    """Tests the get_auth_username function."""

    monkeypatch.setenv("EDX2GIFT_USERNAME", "foo")
    monkeypatch.setenv("EDX2GIFT_PASSWORD", "bar")
    correct_credentials = HTTPBasicCredentials(username="foo", password="bar")
    assert get_auth_username(correct_credentials) == "foo"

    invalid_credentials = HTTPBasicCredentials(username="foo", password="foo")
    with pytest.raises(HTTPException) as exception:
        get_auth_username(invalid_credentials)

    assert exception.value.status_code == 401
    assert exception.value.detail == "Incorrect email or password"
    assert exception.value.headers == {"WWW-Authenticate": "Basic"}

    invalid_credentials = HTTPBasicCredentials(username="bar", password="bar")
    with pytest.raises(HTTPException) as exception:
        get_auth_username(invalid_credentials)

    assert exception.value.status_code == 401
    assert exception.value.detail == "Incorrect email or password"
    assert exception.value.headers == {"WWW-Authenticate": "Basic"}


@pytest.mark.anyio
async def test_api_convert(monkeypatch):
    """Tests the convert endpoint."""
    monkeypatch.setenv("EDX2GIFT_USERNAME", "foo")
    monkeypatch.setenv("EDX2GIFT_PASSWORD", "bar")
    content = "<root><p>foo</p></root>"
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/convert", auth=("foo", "bar"), data={"content": content}
        )
        assert response.status_code == 200
        assert response.content == b""
