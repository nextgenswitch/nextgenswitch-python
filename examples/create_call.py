import os

from nextgenswitch import Client, VoiceResponse

client = Client(
    os.environ["NEXTGENSWITCH_BASE_URL"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION_SECRET"],
)

flow = VoiceResponse().say("Welcome to NextGenSwitch.").gather(
    action="https://example.com/gather",
    method="POST",
    numDigits=1,
    timeout=10,
    children=lambda gather: gather.say("Press one for sales or two for support."),
)

result = client.create_call(
    "2001",
    "1001",
    response_xml=flow,
    status_callback="https://example.com/call-status",
)
print(result.data)
client.close()
