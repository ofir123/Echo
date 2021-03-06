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
    if intent_name in ['CinemaPlayIntent', 'CinemaStopIntent', 'CinemaOnIntent', 'CinemaOffIntent']:
        return handle_cinema(intent)
    else:
        raise ValueError('Invalid intent')


def on_session_ended(session_ended_request, session):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true.
    """
    print('on_session_ended requestId=' + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])

# --------------- Functions that control the skill's behavior ------------------


def handle_cinema(intent):
    """
    Start Cinema mode and try to play the selected term.
    and prepares the speech to reply to the user.
    """
    card_title = intent['name']
    intent_slots = intent.get('slots')
    # Initialize control server connection.
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect('tcp://{}:{}'.format(CONTROL_SERVER_HOST, CONTROL_SERVER_PORT))
    # Get search term.
    if card_title == 'CinemaPlayIntent' and intent_slots and 'Show' in intent_slots and 'Season' in intent_slots and \
            'Episode' in intent_slots:
        show = intent['slots']['Show']['value']
        season = intent['slots']['Season']['value']
        episode = intent['slots']['Episode']['value']
        if show and season and episode:
            print('Playing {}, season {}, episode {}'.format(show, season, episode))
            # TV part.
            socket.send_string('TV_ON')
            # Receiver part.
            socket.send_string('RECEIVER_ON_SURROUND')
            # Set audio output to receiver.
            socket.send_string('SOUND_RECEIVER')
            # Try and find the correct show path, and play it.
            socket.send_string('VIDEO_PLAY_{}_{}_{}'.format(show, season, episode))
            # Set response.
            speech_output = 'Playing {}, season {}, episode {}. Enjoy!'.format(show, season, episode)
            reprompt_text = 'I said, playing {}, season {}, episode {}!'.format(show, season, episode)
        else:
            # Set response.
            speech_output = 'What should I play?'
            reprompt_text = 'You need to state show name, season number and episode number!'
        print('Success!')
    elif card_title == 'CinemaStopIntent':
        print('Stopping current show')
        # Close YouTube.
        socket.send_string('VIDEO_STOP')
        # Set response.
        speech_output = 'Stopped playing.'
        reprompt_text = 'I said, stopped playing!'
        print('Success!')
    elif card_title == 'CinemaOnIntent':
        print('Turning Cinema mode on')
        # TV part.
        socket.send_string('TV_ON')
        # Receiver part.
        socket.send_string('RECEIVER_ON_SURROUND')
        # Set audio output to computer.
        socket.send_string('SOUND_RECEIVER')
        # Set response.
        speech_output = 'Turning cinema mode on'
        reprompt_text = 'I said, cinema mode is on!'
        print('Success!')
    elif card_title == 'CinemaOffIntent':
        print('Turning Cinema mode off')
        # TV part.
        socket.send_string('TV_OFF')
        # Receiver part.
        socket.send_string('RECEIVER_OFF')
        # Set audio output to computer.
        socket.send_string('SOUND_COMPUTER')
        # Set response.
        speech_output = 'Turning cinema mode off'
        reprompt_text = 'I said, cinema mode is turned off!'
        print('Success!')
    else:
        # Set response.
        speech_output = 'Do you want me to stop or play?'
        reprompt_text = 'You need to say: stop/play something!'
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
