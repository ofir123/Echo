from __future__ import print_function

import zmq

# TV server details.
CONTROL_SERVER_HOST = 'casagabirol.hopto.org'
CONTROL_SERVER_PORT = '9999'


def lambda_handler(event, _):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print('event.session.application.applicationId=' + event['session']['application']['applicationId'])
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
    if event['request']['type'] == 'LaunchRequest':
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == 'IntentRequest':
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == 'SessionEndedRequest':
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """
    Called when the session starts.
    """
    print('on_session_started requestId=' + session_started_request['requestId'] + ', sessionId=' +
          session['sessionId'])


def on_launch(launch_request, session):
    """
    Called when the user launches the skill without specifying what they want.
    """
    print('on_launch requestId=' + launch_request['requestId'] + ', sessionId=' + session['sessionId'])


def on_intent(intent_request, session):
    """
    Called when the user specifies an intent for this skill.
    """
    print('on_intent requestId=' + intent_request['requestId'] + ', sessionId=' + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    # Dispatch to your skill's intent handlers.
    if intent_name in ['TVOnIntent', 'TVOffIntent']:
        return handle_tv(intent)
    else:
        raise ValueError('Invalid intent')


def on_session_ended(session_ended_request, session):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true.
    """
    print('on_session_ended requestId=' + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])

# --------------- Functions that control the skill's behavior ------------------


def handle_tv(intent):
    """
    Apply the requested function on the TV,
    and prepares the speech to reply to the user.
    """
    card_title = intent['name']
    # Initialize control server connection.
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect('tcp://{}:{}'.format(CONTROL_SERVER_HOST, CONTROL_SERVER_PORT))
    if card_title == 'TVOnIntent':
        print('Turning TV on')
        # Receiver part.
        socket.send_string('TV_ON')
        # Set response.
        speech_output = 'Turning TV on'
        reprompt_text = 'The TV is now on'
        print('Success!')
    elif card_title == 'TVOffIntent':
        print('Turning TV off')
        socket.send_string('TV_OFF')
        # Set response.
        speech_output = 'Turning TV off'
        reprompt_text = 'The TV is now turned off'
        print('Success!')
    else:
        # Set response.
        speech_output = 'What exactly do you want me to do?'
        reprompt_text = 'Explain what do you want me to do!'
    return build_speechlet_response(card_title, speech_output, reprompt_text)

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text):
    return {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'card': {
                'type': 'Simple',
                'title': 'SessionSpeechlet - ' + title,
                'content': 'SessionSpeechlet - ' + output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': True
        }
    }
