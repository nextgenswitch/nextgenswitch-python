"""Safe builder for NextGenSwitch Voice XML."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional
from xml.etree import ElementTree as ET


def _attributes(values: Mapping[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for name, value in values.items():
        if value is None:
            continue
        if isinstance(value, bool):
            normalized[name] = "true" if value else "false"
        else:
            normalized[name] = str(value)
    return normalized


class VoiceNode:
    """A restricted nested node used inside Gather and Dial."""

    def __init__(self, element: ET.Element) -> None:
        self._element = element

    def say(self, text: str, **attributes: Any) -> VoiceNode:
        child = ET.SubElement(self._element, "Say", _attributes(attributes))
        child.text = text
        return self

    def play(self, url: str, **attributes: Any) -> VoiceNode:
        child = ET.SubElement(self._element, "Play", _attributes(attributes))
        child.text = url
        return self


class VoiceResponse:
    """Fluent, XML-escaping builder for documented NextGenSwitch voice verbs."""

    def __init__(self) -> None:
        self._root = ET.Element("Response")

    def say(self, text: str, **attributes: Any) -> VoiceResponse:
        child = ET.SubElement(self._root, "Say", _attributes(attributes))
        child.text = text
        return self

    def play(self, url: str, **attributes: Any) -> VoiceResponse:
        child = ET.SubElement(self._root, "Play", _attributes(attributes))
        child.text = url
        return self

    def gather(
        self,
        *,
        children: Optional[Callable[[VoiceNode], None]] = None,
        **attributes: Any,
    ) -> VoiceResponse:
        element = ET.SubElement(self._root, "Gather", _attributes(attributes))
        if children is not None:
            children(VoiceNode(element))
        return self

    def dial(
        self,
        to: str,
        *,
        children: Optional[Callable[[VoiceNode], None]] = None,
        **attributes: Any,
    ) -> VoiceResponse:
        element = ET.SubElement(self._root, "Dial", _attributes({"to": to, **attributes}))
        if children is not None:
            children(VoiceNode(element))
        return self

    def record(self, **attributes: Any) -> VoiceResponse:
        ET.SubElement(self._root, "Record", _attributes(attributes))
        return self

    def stream(
        self,
        url: str,
        *,
        parameters: Optional[Mapping[str, Any]] = None,
        **attributes: Any,
    ) -> VoiceResponse:
        connect = ET.SubElement(self._root, "Connect")
        stream = ET.SubElement(connect, "Stream", _attributes({"url": url, **attributes}))
        for name, value in (parameters or {}).items():
            ET.SubElement(stream, "Parameter", _attributes({"name": name, "value": value}))
        return self

    def hangup(self) -> VoiceResponse:
        ET.SubElement(self._root, "Hangup")
        return self

    def pause(self, length: int) -> VoiceResponse:
        if length < 0:
            raise ValueError("Pause length cannot be negative.")
        ET.SubElement(self._root, "Pause", {"length": str(length)})
        return self

    def redirect(self, url: str, *, method: str = "POST") -> VoiceResponse:
        element = ET.SubElement(self._root, "Redirect", {"method": method.upper()})
        element.text = url
        return self

    def bridge(self, call_id: str, *, bridge_after_establish: bool = True) -> VoiceResponse:
        element = ET.SubElement(
            self._root,
            "Bridge",
            {"bridgeAfterEstablish": "true" if bridge_after_establish else "false"},
        )
        element.text = call_id
        return self

    def leave(self) -> VoiceResponse:
        ET.SubElement(self._root, "Leave")
        return self

    def to_xml(self) -> str:
        body = ET.tostring(self._root, encoding="unicode", short_empty_elements=True)
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + body

    def __str__(self) -> str:
        return self.to_xml()
