"""Typed callback payloads from Gather and Dial actions."""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class GatherResult:
    call_id: str
    digits: Optional[str] = None
    speech_result: Optional[str] = None
    confidence: Optional[float] = None
    voice: Optional[str] = None
    from_: Optional[str] = None
    to: Optional[str] = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "GatherResult":
        confidence = payload.get("confidence")
        confidence_value: Optional[float] = None
        if confidence is not None and confidence != "":
            confidence_value = float(str(confidence))
        return cls(
            call_id=str(payload.get("call_id", "")),
            digits=str(payload["digits"]) if "digits" in payload else None,
            speech_result=str(payload["speech_result"]) if "speech_result" in payload else None,
            confidence=confidence_value,
            voice=str(payload["voice"]) if "voice" in payload else None,
            from_=str(payload["event_from"]) if "event_from" in payload else None,
            to=str(payload["event_to"]) if "event_to" in payload else None,
        )


@dataclass(frozen=True)
class DialResult:
    call_id: str
    bridge_call_id: Optional[str]
    established: bool
    duration: int
    waiting_duration: int
    record_file: Optional[str]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "DialResult":
        return cls(
            call_id=str(payload.get("call_id", "")),
            bridge_call_id=(
                str(payload["bridge_call_id"]) if payload.get("bridge_call_id") else None
            ),
            established=int(payload.get("dial_status", 0)) == 1,
            duration=int(payload.get("duration", 0)),
            waiting_duration=int(payload.get("waiting_duration", 0)),
            record_file=str(payload["record_file"]) if payload.get("record_file") else None,
        )
