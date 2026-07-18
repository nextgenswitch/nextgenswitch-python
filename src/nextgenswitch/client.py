"""Synchronous and asynchronous clients for the NextGenSwitch Voice API."""

from __future__ import annotations

from typing import Any, Optional, Union
from urllib.parse import quote

import httpx

from .exceptions import ApiError, TransportError, ValidationError
from .responses import ApiResponse
from .voice import VoiceResponse

VoiceXml = Union[VoiceResponse, str]


def _validate_configuration(base_url: str, authorization: str, secret: str) -> str:
    normalized = base_url.rstrip("/")
    if not normalized or not authorization or not secret:
        raise ValidationError("Base URL and both authorization values are required.")
    return normalized


def _call_payload(
    to: str,
    from_: str,
    response_xml: Optional[VoiceXml],
    response_url: Optional[str],
    status_callback: Optional[str],
) -> dict[str, str]:
    if not to or not from_:
        raise ValidationError("The to and from_ values are required.")
    if (response_xml is None) == (response_url is None):
        raise ValidationError("Provide exactly one of response_xml or response_url.")

    payload = {"to": to, "from": from_}
    if response_xml is not None:
        payload["responseXml"] = str(response_xml)
    if response_url is not None:
        payload["response"] = response_url
    if status_callback is not None:
        payload["statusCallback"] = status_callback
    return payload


def _api_response(response: httpx.Response) -> ApiResponse:
    try:
        decoded: Any = response.json()
    except ValueError:
        decoded = None
    data = decoded if isinstance(decoded, dict) else None
    if not response.is_success:
        message = str(data.get("message")) if data and "message" in data else (
            f"NextGenSwitch API returned HTTP {response.status_code}."
        )
        raise ApiError(message, response.status_code, response.text)
    return ApiResponse(response.status_code, data, response.text)


class Client:
    """Blocking NextGenSwitch API client."""

    def __init__(
        self,
        base_url: str,
        authorization: str,
        authorization_secret: str,
        *,
        timeout: float = 30.0,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.base_url = _validate_configuration(base_url, authorization, authorization_secret)
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=timeout)
        self._headers = {
            "Accept": "application/json",
            "X-Authorization": authorization,
            "X-Authorization-Secret": authorization_secret,
        }

    def create_call(
        self,
        to: str,
        from_: str,
        *,
        response_xml: Optional[VoiceXml] = None,
        response_url: Optional[str] = None,
        status_callback: Optional[str] = None,
    ) -> ApiResponse:
        payload = _call_payload(to, from_, response_xml, response_url, status_callback)
        return self._request("POST", "/api/v1/call", data=payload)

    def modify_call(self, call_id: str, response_xml: VoiceXml) -> ApiResponse:
        if not call_id:
            raise ValidationError("Call ID is required.")
        return self._request(
            "PUT",
            f"/api/v1/call/{quote(call_id, safe='')}",
            json={"responseXml": str(response_xml)},
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> ApiResponse:
        try:
            response = self._client.request(
                method, self.base_url + path, headers=self._headers, **kwargs
            )
        except httpx.HTTPError as exc:
            raise TransportError(f"NextGenSwitch request failed: {exc}") from exc
        return _api_response(response)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncClient:
    """Async NextGenSwitch API client."""

    def __init__(
        self,
        base_url: str,
        authorization: str,
        authorization_secret: str,
        *,
        timeout: float = 30.0,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.base_url = _validate_configuration(base_url, authorization, authorization_secret)
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(timeout=timeout)
        self._headers = {
            "Accept": "application/json",
            "X-Authorization": authorization,
            "X-Authorization-Secret": authorization_secret,
        }

    async def create_call(
        self,
        to: str,
        from_: str,
        *,
        response_xml: Optional[VoiceXml] = None,
        response_url: Optional[str] = None,
        status_callback: Optional[str] = None,
    ) -> ApiResponse:
        payload = _call_payload(to, from_, response_xml, response_url, status_callback)
        return await self._request("POST", "/api/v1/call", data=payload)

    async def modify_call(self, call_id: str, response_xml: VoiceXml) -> ApiResponse:
        if not call_id:
            raise ValidationError("Call ID is required.")
        return await self._request(
            "PUT",
            f"/api/v1/call/{quote(call_id, safe='')}",
            json={"responseXml": str(response_xml)},
        )

    async def _request(self, method: str, path: str, **kwargs: Any) -> ApiResponse:
        try:
            response = await self._client.request(
                method, self.base_url + path, headers=self._headers, **kwargs
            )
        except httpx.HTTPError as exc:
            raise TransportError(f"NextGenSwitch request failed: {exc}") from exc
        return _api_response(response)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
