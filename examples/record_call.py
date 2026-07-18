import os

from nextgenswitch import Client, VoiceResponse

client = Client(
    os.environ["NEXTGENSWITCH_BASE_URL"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION_SECRET"],
)
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
    .say("Thank you. Goodbye.")
    .hangup()
)
print(client.create_call("2001", "1001", response_xml=flow).data)
client.close()
