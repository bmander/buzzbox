
import functions_framework
from twilio.twiml.voice_response import VoiceResponse, Gather
import google.cloud.logging
import logging
from flask import make_response

from markupsafe import escape
import re
import os

client = google.cloud.logging.Client()
client.setup_logging()

VALID_CODES = [
    'ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO', 'FOXTROT', 'GOLF', 'HOTEL',
    'INDIA', 'JULIETT', 'KILO', 'LIMA', 'MIKE', 'NOVEMBER', 'OSCAR', 'PAPA',
    'QUEBEC', 'ROMEO', 'SIERRA', 'TANGO', 'UNIFORM', 'VICTOR', 'WHISKEY',
    'XRAY', 'YANKEE', 'ZULU'
]

WHITELIST = ["+12069927567", "+12063250546"]

DOORCODES = {("WHISKEY", "TANGO", "FOXTROT"), ("KILO", "LIMA", "MIKE")}

def make_code(words):
    """Remove punctuation, convert to uppercase, and split into words."""
    return tuple(re.sub(r'[^\w\s]', '', words).upper().split())


@functions_framework.http
def voice(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    # Start our TwiML response
    resp = VoiceResponse()


    from_number = request.values.get('From')
    logging.info(f"Call from {from_number}")

    if from_number not in WHITELIST:
        logging.info(f"Rejecting call; not on whitelist")
        resp.reject()
        return str(resp)
    
    resp.pause(length=0.5)

    call_sid = request.values.get('CallSid')

    attempts = int(request.cookies.get(f'attempts_{call_sid}', 0))

    if 'SpeechResult' in request.values:
        transcript = request.values.get('SpeechResult')
        logging.info(f"transcript = {transcript}")
        
        spoken_code = make_code(transcript)

        if spoken_code in DOORCODES:
            resp.say("Access granted", voice="Google.en-US-Standard-A", language="en-US")
            resp.pause(length=0.2)
            resp.play("", digits="9")
        else:
            resp.say("Access denied", voice="Google.en-US-Standard-A", language="en-US")

            attempts += 1

            if attempts < 3:
                resp.say("you said " + " ".join(spoken_code), voice="Google.en-US-Standard-A", language="en-US")
                gather = Gather(input='speech', 
                                language='en-US',
                                hints=','.join(VALID_CODES),
                                timeout=5,
                                speechTimeout="auto")
                gather.say("Please try again", voice="Google.en-US-Standard-A", language="en-US")
                resp.append(gather)
            else:
                resp.say("Too many attempts. Goodbye.")
    else:
        gather = Gather(input='speech', 
                        language='en-US',
                        hints=','.join(VALID_CODES),
                        timeout=5,
                        speechTimeout="auto")
        gather.say("Speak the code CLEAR and LOUD", voice="Google.en-US-Standard-A", language="en-US")
        resp.append(gather)

    response = make_response(str(resp))

    response.set_cookie(f'attempts_{call_sid}', str(attempts), max_age=3600, secure=True)

    return response
