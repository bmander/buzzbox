import functions_framework
from twilio.twiml.voice_response import VoiceResponse, Gather
import google.cloud.logging
import logging
from flask import make_response
import re
import os
import yaml

def load_config():
    """Load configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# Load configuration
CONFIG = load_config()

DOOR_CODES = {tuple(code.upper().split()) for code in CONFIG['door_codes']}

def make_code(words):
    """Remove punctuation, convert to uppercase, and split into words."""
    return tuple(re.sub(r'[^\w\s]', '', words).upper().split())

@functions_framework.http
def voice(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
    Returns:
        Response object from Flask's make_response.
    """
    # Start our TwiML response
    resp = VoiceResponse()

    from_number = request.values.get('From')
    logging.info(f"Call from {from_number}")

    if from_number not in CONFIG['whitelist']:
        logging.info(f"Rejecting call; not on whitelist")
        resp.reject()
        return str(resp)
    

    call_sid = request.values.get('CallSid')
    attempts = int(request.cookies.get(f'attempts_{call_sid}', 0))

    if 'SpeechResult' in request.values:
        transcript = request.values.get('SpeechResult')
        logging.info(f"transcript = {transcript}")

        spoken_code = make_code(transcript)

        if spoken_code in DOOR_CODES:
            resp.say(CONFIG['messages']['access_granted'], 
                    voice=CONFIG['voice_settings']['voice_name'], 
                    language=CONFIG['voice_settings']['language'])
            resp.pause(length=CONFIG['success_pause'])
            resp.play("", digits="9")
        else:
            resp.say(CONFIG['messages']['access_denied'],
                    voice=CONFIG['voice_settings']['voice_name'],
                    language=CONFIG['voice_settings']['language'])

            attempts += 1

            if attempts < CONFIG['max_attempts']:
                resp.say("you said " + " ".join(spoken_code),
                        voice=CONFIG['voice_settings']['voice_name'],
                        language=CONFIG['voice_settings']['language'])
                gather = Gather(input='speech',
                              language=CONFIG['voice_settings']['language'],
                              hints=','.join(CONFIG['valid_codes']),
                              timeout=CONFIG['voice_settings']['gather_timeout'],
                              speechTimeout=CONFIG['voice_settings']['speech_timeout'])
                gather.say(CONFIG['messages']['try_again'],
                         voice=CONFIG['voice_settings']['voice_name'],
                         language=CONFIG['voice_settings']['language'])
                resp.append(gather)
            else:
                resp.say(CONFIG['messages']['too_many_attempts'],
                        voice=CONFIG['voice_settings']['voice_name'],
                        language=CONFIG['voice_settings']['language'])
    else:
        resp.pause(length=CONFIG['initial_pause'])
        gather = Gather(input='speech',
                       language=CONFIG['voice_settings']['language'],
                       hints=','.join(CONFIG['valid_codes']),
                       timeout=CONFIG['voice_settings']['gather_timeout'],
                       speechTimeout=CONFIG['voice_settings']['speech_timeout'])
        gather.say(CONFIG['messages']['speak_code'],
                  voice=CONFIG['voice_settings']['voice_name'],
                  language=CONFIG['voice_settings']['language'])
        resp.append(gather)

    httpresp = make_response(str(resp))
    httpresp.set_cookie(f'attempts_{call_sid}',
                       str(attempts),
                       max_age=CONFIG['cookie_max_age'],
                       secure=True)

    return httpresp