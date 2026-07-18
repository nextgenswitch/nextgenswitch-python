# NextGenSwitch Python SDK

[![Tests](https://github.com/nextgenswitch/nextgenswitch-python/actions/workflows/tests.yml/badge.svg)](https://github.com/nextgenswitch/nextgenswitch-python/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

The official Python SDK for the [NextGenSwitch Programmable Voice API](https://nextgenswitch.com/docs/programmable-voice-api/). Create and modify calls with synchronous or asynchronous clients, build escaped Voice XML, stream audio to AI services, and parse Gather and Dial callbacks.

## Requirements

- Python 3.9 or newer
- A NextGenSwitch deployment and API credentials

## Installation

```bash
pip install nextgenswitch
```

Until the first PyPI release, install from GitHub:

```bash
pip install "nextgenswitch @ git+https://github.com/nextgenswitch/nextgenswitch-python.git"
```

## Configure the Client

```python
import os
from nextgenswitch import Client

client = Client(
    os.environ["NEXTGENSWITCH_BASE_URL"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION_SECRET"],
)
```

The SDK sends the documented `X-Authorization` and `X-Authorization-Secret` headers. Keep these values in environment variables or a secret manager and use HTTPS for remote deployments.

## Create a Call

```python
from nextgenswitch import VoiceResponse

flow = VoiceResponse().say("Welcome to NextGenSwitch.").gather(
    action="https://example.com/gather",
    method="POST",
    numDigits=1,
    timeout=10,
    children=lambda gather: gather.say("Press one for sales."),
)

result = client.create_call(
    "2001",
    "1001",
    response_xml=flow,
    status_callback="https://example.com/call-status",
)
print(result.data)
```

Use `response_url="https://example.com/call-flow.xml"` instead of `response_xml` to provide a hosted XML document. Exactly one response source is required.

## Modify an Active Call

```python
updated = (
    VoiceResponse()
    .pause(2)
    .say("Your call flow has been updated.")
    .dial("1000", answerOnBridge=True)
)

client.modify_call("CALL-123", updated)
```

## Async Client

```python
import asyncio
import os

from nextgenswitch import AsyncClient, VoiceResponse

async def main() -> None:
    async with AsyncClient(
        os.environ["NEXTGENSWITCH_BASE_URL"],
        os.environ["NEXTGENSWITCH_AUTHORIZATION"],
        os.environ["NEXTGENSWITCH_AUTHORIZATION_SECRET"],
    ) as client:
        result = await client.create_call(
            "2001",
            "1001",
            response_xml=VoiceResponse().say("Hello from async Python."),
        )
        print(result.data)

asyncio.run(main())
```

## Voice XML

| XML verb | Python method |
| --- | --- |
| `<Say>` | `say(text, **attributes)` |
| `<Play>` | `play(url, **attributes)` |
| `<Gather>` | `gather(children=..., **attributes)` |
| `<Dial>` | `dial(to, children=..., **attributes)` |
| `<Record>` | `record(**attributes)` |
| `<Connect><Stream>` | `stream(url, parameters=..., **attributes)` |
| `<Hangup>` | `hangup()` |
| `<Pause>` | `pause(seconds)` |
| `<Redirect>` | `redirect(url, method=...)` |
| `<Bridge>` | `bridge(call_id, bridge_after_establish=...)` |
| `<Leave>` | `leave()` |

Python's XML library escapes text and attributes instead of concatenating untrusted XML strings.

## Record a Call

```python
flow = (
    VoiceResponse()
    .say("Please leave your message after the beep.")
    .record(
        action="https://example.com/recording",
        method="POST",
        timeout=5,
        finishOnKey="#",
        transcribe=True,
        trim=True,
        beep=True,
    )
    .hangup()
)
client.create_call("2001", "1001", response_xml=flow)
```

## Stream to an AI Voice Service

```python
flow = VoiceResponse().stream(
    "wss://voice.example.com/session",
    parameters={"session_id": "session-123", "tenant": "example"},
    name="assistant-stream",
)
```

Resolve AI-provider secrets on the WebSocket service. Never put provider API keys in Voice XML.

## Parse Webhooks

```python
from nextgenswitch import GatherResult

gather = GatherResult.from_mapping(request.form)
if gather.digits == "1":
    response = VoiceResponse().say("Connecting sales.").dial("1001")
else:
    response = VoiceResponse().say("No valid selection received.").hangup()
```

Use `DialResult.from_mapping(payload)` for documented Dial action fields. Callback signature verification is not documented by the current API; restrict endpoints, require TLS, validate expected fields, and add deployment-appropriate authentication.

## Errors

- `ValidationError`: invalid SDK input
- `ApiError`: non-2xx response, with `status_code` and `response_body`
- `TransportError`: network or HTTP transport failure
- `NextGenSwitchError`: base SDK exception

## Examples

Configure `NEXTGENSWITCH_BASE_URL`, `NEXTGENSWITCH_AUTHORIZATION`, and `NEXTGENSWITCH_AUTHORIZATION_SECRET`, then adapt:

- [Create call](examples/create_call.py)
- [Modify active call](examples/modify_call.py)
- [Record caller audio](examples/record_call.py)
- [Stream to AI](examples/stream_to_ai.py)

All `example.com` URLs are placeholders for TLS endpoints you control.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check .
mypy src/nextgenswitch
pytest
python -m build
python -m twine check dist/*
```

GitHub Actions validates Python 3.9–3.13.

## Documentation

- [Programmable Voice API](https://nextgenswitch.com/docs/programmable-voice-api/)
- [NextGenSwitch documentation](https://nextgenswitch.com/docs/)
- [NextGenSwitch website](https://nextgenswitch.com/)
- [Contact NextGenSwitch](https://nextgenswitch.com/contact/)

## License

[MIT](LICENSE)
