import asyncio

import httpx

from nextgenswitch import AsyncClient, VoiceResponse


def test_async_create_call() -> None:
    async def run() -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["X-Authorization-Secret"] == "secret"
            return httpx.Response(201, json={"call_id": "CALL-ASYNC"})

        http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        client = AsyncClient("https://switch.example.com", "code", "secret", http_client=http)
        result = await client.create_call(
            "2001", "1001", response_xml=VoiceResponse().say("Hello")
        )
        assert result.data == {"call_id": "CALL-ASYNC"}
        await http.aclose()

    asyncio.run(run())
