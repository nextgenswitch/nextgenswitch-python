import os
import sys

from nextgenswitch import Client, VoiceResponse

if len(sys.argv) != 2:
    raise SystemExit("Usage: python examples/modify_call.py CALL_ID")

client = Client(
    os.environ["NEXTGENSWITCH_BASE_URL"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION"],
    os.environ["NEXTGENSWITCH_AUTHORIZATION_SECRET"],
)
flow = VoiceResponse().pause(1).say("Your call flow has been updated.").dial(
    "1000", answerOnBridge=True, timeLimit=300
)
result = client.modify_call(sys.argv[1], flow)
print(result.data)
client.close()
