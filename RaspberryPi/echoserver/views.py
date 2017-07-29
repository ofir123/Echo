import os

import ujson
import requests
import logbook
import rxv
from flask import Blueprint, make_response

from . import config

app_views = Blueprint('app_views', __name__)

logger = logbook.Logger(__name__)

# Set a persistent computer session.
computer_session = requests.Session()
computer_session.verify = 'certs/echo-server.cert'

receiver = rxv.RXV('http://{}:80/YamahaRemoteControl/ctrl'.format(config.RECEIVER_IP), 'RX-V671')


def _make_error_response(error_string):
    """
    Return an error response to the user.

    :param error_string: The error string to write.
    :return: The server error response.
    """
    logger.error(error_string)
    return make_response(ujson.dumps({'error': error_string}))


@app_views.route('/tv/on', methods=['GET'])
def tv_on():
    logger.info('Turning TV on!')
    os.system('echo "on 0" | cec-client -s')
    return ''


@app_views.route('/tv/off', methods=['GET'])
def tv_off():
    logger.info('Turning TV off!')
    os.system('echo "standby 0" | cec-client -s')
    return ''


def _turn_receiver_on():
    """
    A simple utility function for turning on the receiver.
    """
    if not receiver.on:
        receiver.on = True
    # Set input.
    if receiver.input != config.DEFAULT_INPUT:
        receiver.input = config.DEFAULT_INPUT
    # Set sound output to receiver using the computer.
    computer_session.get('{}/audio/receiver'.format(config.COMPUTER_URL))


@app_views.route('/receiver/on', methods=['GET'])
def receiver_on():
    logger.info('Turning the receiver on')
    _turn_receiver_on()
    return ''


@app_views.route('/receiver/on/surround', methods=['GET'])
def receiver_on_surround():
    logger.info('Turning the receiver on surround mode')
    _turn_receiver_on()
    # Set surround mode.
    request_text = '<Surround><Program_Sel><Current><Straight>Off</Straight><Sound_Program>Surround Decoder' \
                   '</Sound_Program></Current></Program_Sel></Surround>'
    receiver._request('PUT', request_text)
    # Set volume.
    if receiver.volume != config.DEFAULT_SURROUND_VOLUME:
        receiver.volume = config.DEFAULT_SURROUND_VOLUME
    return ''


@app_views.route('/receiver/on/music', methods=['GET'])
def receiver_on_music():
    logger.info('Turning the receiver on music mode')
    _turn_receiver_on()
    # Set music mode.
    request_text = '<Surround><Program_Sel><Current><Sound_Program>7ch Stereo</Sound_Program>' \
                   '</Current></Program_Sel></Surround>'
    receiver._request('PUT', request_text)
    # Set volume.
    if receiver.volume != config.DEFAULT_MUSIC_VOLUME:
        receiver.volume = config.DEFAULT_MUSIC_VOLUME
    return ''


@app_views.route('/receiver/volume/up', methods=['GET'])
def receiver_volume_up():
    logger.info('Turning receiver volume up')
    if receiver.on:
        receiver.volume += config.VOLUME_UNIT
    return ''


@app_views.route('/receiver/volume/down', methods=['GET'])
def receiver_volume_down():
    logger.info('Turning receiver volume down')
    if receiver.on:
        receiver.volume -= config.VOLUME_UNIT
    return ''


@app_views.route('/receiver/off', methods=['GET'])
def receiver_off():
    logger.info('Turning the receiver off')
    if receiver.on:
        receiver.on = False
    # Set sound output back to computer using the computer.
    computer_session.get('{}/audio/computer'.format(config.COMPUTER_URL))
    return ''

# Computer Proxy Views


@app_views.route('/audio/receiver', methods=['GET'])
def set_audio_receiver():
    # Set audio output to receiver.
    logger.info('Setting audio device to receiver')
    computer_session.get('{}/audio/receiver'.format(config.COMPUTER_URL))
    return ''


@app_views.route('/audio/computer', methods=['GET'])
def set_audio_computer():
    # Set audio output to computer.
    logger.info('Setting audio device to computer')
    computer_session.get('{}/audio/computer'.format(config.COMPUTER_URL))
    return ''


@app_views.route('/youtube/play/<term>', methods=['GET'])
def youtube_play(term):
    if not term:
        _make_error_response('Must supply a term for YouTube to play!')
    logger.info('Playing {} on YouTube!'.format(term))
    computer_session.get('{}/youtube/play/{}'.format(config.COMPUTER_URL, term))
    return ''


@app_views.route('/youtube/resume', methods=['GET'])
def youtube_resume():
    logger.info('Resuming YouTube video!')
    computer_session.get('{}/youtube/resume'.format(config.COMPUTER_URL))
    return ''


@app_views.route('/youtube/pause', methods=['GET'])
def youtube_pause():
    logger.info('Pausing YouTube video!')
    computer_session.get('{}/youtube/pause'.format(config.COMPUTER_URL))
    return ''


@app_views.route('/youtube/next', methods=['GET'])
def youtube_next():
    logger.info('Playing the next video on YouTube!')
    computer_session.get('{}/youtube/next'.format(config.COMPUTER_URL))
    return ''


@app_views.route('/youtube/stop', methods=['GET'])
def youtube_stop():
    logger.info('Stopping YouTube!')
    computer_session.get('{}/youtube/stop'.format(config.COMPUTER_URL))
    return ''
