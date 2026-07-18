from xml.etree import ElementTree as ET

import pytest

from nextgenswitch import VoiceResponse


def test_builds_escaped_voice_xml() -> None:
    response = (
        VoiceResponse()
        .say("Sales & support", loop=2)
        .gather(
            action="https://example.com/input",
            input="dtmf speech",
            numDigits=1,
            children=lambda node: node.say("Press <one>"),
        )
        .dial("+15551234567", answerOnBridge=True)
        .pause(2)
        .hangup()
    )

    root = ET.fromstring(response.to_xml())
    assert root.tag == "Response"
    assert "Sales &amp; support" in response.to_xml()
    assert 'answerOnBridge="true"' in response.to_xml()


def test_builds_stream_parameters() -> None:
    xml = VoiceResponse().stream(
        "wss://voice.example.com/ws", parameters={"session": "abc"}, name="assistant"
    ).to_xml()

    assert "<Connect>" in xml
    assert 'url="wss://voice.example.com/ws"' in xml
    assert 'name="session" value="abc"' in xml


def test_rejects_negative_pause() -> None:
    with pytest.raises(ValueError):
        VoiceResponse().pause(-1)
