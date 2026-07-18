import os
import secrets

from nextgenswitch import Client, VoiceResponse

client = Client(
    os.environ["NEXTGENSWITCH_BASE_URL"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION_SECRET"],
)
flow = VoiceResponse().say("Connecting the virtual assistant.").stream(
    "wss://voice.example.com/session",
    parameters={"session_id": secrets.token_hex(16), "tenant": "example"},
    name="ai-assistant",
)
print(client.create_call("2001", "1001", response_xml=flow).data)
client.close()

# Resolve AI-provider credentials on the WebSocket service, not in Voice XML.
