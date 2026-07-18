from nextgenswitch import DialResult, GatherResult


def test_parses_gather_callback() -> None:
    result = GatherResult.from_mapping(
        {"call_id": "C1", "digits": "1234", "confidence": "0.95"}
    )
    assert result.call_id == "C1"
    assert result.digits == "1234"
    assert result.confidence == 0.95


def test_parses_dial_callback() -> None:
    result = DialResult.from_mapping(
        {"call_id": "C1", "dial_status": "1", "duration": "84"}
    )
    assert result.established is True
    assert result.duration == 84
