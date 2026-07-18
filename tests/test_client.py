import json

import httpx
import pytest

from nextgenswitch import ApiError, Client, ValidationError, VoiceResponse


def test_creates_call_with_authentication_and_xml() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(201, json={"call_id": "CALL-123"})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = Client("https://switch.example.com/", "code", "secret", http_client=http)
    result = client.create_call("2001", "1001", response_xml=VoiceResponse().say("Hello"))

    assert result.status_code == 201
    assert result.data == {"call_id": "CALL-123"}
    assert captured[0].headers["X-Authorization"] == "code"
    assert "responseXml=" in captured[0].content.decode()


def test_modifies_encoded_call_id() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"updated": True})

    client = Client(
        "https://switch.example.com",
        "code",
        "secret",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    client.modify_call("CALL/123", VoiceResponse().hangup())

    assert captured[0].url.path == "/api/v1/call/CALL/123"
    assert json.loads(captured[0].content)["responseXml"].startswith("<?xml")


def test_rejects_ambiguous_response_source() -> None:
    client = Client("https://switch.example.com", "code", "secret")
    with pytest.raises(ValidationError):
        client.create_call("2", "1")
    client.close()


def test_raises_typed_api_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "Unauthorized"})

    client = Client(
        "https://switch.example.com",
        "code",
        "secret",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    with pytest.raises(ApiError) as caught:
        client.modify_call("CALL-123", VoiceResponse().hangup())

    assert caught.value.status_code == 401
    assert str(caught.value) == "Unauthorized"
