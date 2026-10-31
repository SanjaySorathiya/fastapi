import re

import pytest


@pytest.mark.parametrize("path", ["/menu", "/menu/1", "/menu?category=coffee"])
def test_menu_responses_have_etag_and_cache_control(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert re.fullmatch(r'"[0-9a-f]{64}"', response.headers["etag"])
    assert response.headers["cache-control"] == "max-age=60"


def test_same_request_returns_same_etag(client):
    assert client.get("/menu").headers["etag"] == client.get("/menu").headers["etag"]


def test_different_content_returns_different_etag(client):
    assert (
        client.get("/menu/1").headers["etag"] != client.get("/menu/2").headers["etag"]
    )


def test_matching_if_none_match_returns_304_with_empty_body(client):
    etag = client.get("/menu").headers["etag"]
    response = client.get("/menu", headers={"If-None-Match": etag})
    assert response.status_code == 304
    assert response.content == b""
    assert response.headers["etag"] == etag
    assert response.headers["cache-control"] == "max-age=60"


def test_stale_if_none_match_returns_full_body(client):
    response = client.get("/menu", headers={"If-None-Match": '"stale"'})
    assert response.status_code == 200
    assert response.json()["count"] == 10


@pytest.mark.parametrize("path", ["/", "/health"])
def test_non_menu_routes_have_no_etag(client, path):
    assert "etag" not in client.get(path).headers


@pytest.mark.parametrize("path", ["/menu/999", "/menu/abc", "/menu?category=bad"])
def test_error_responses_have_no_etag(client, path):
    response = client.get(path)
    assert response.status_code >= 400
    assert "etag" not in response.headers
