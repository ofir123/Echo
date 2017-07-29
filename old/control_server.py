import os
import sys

import logbook
import rxv
import zmq

# Control server details.
PORT = '6666'
# Media server details.
MEDIA_SERVER_IP = '192.168.10.10'
MEDIA_SERVER_PORT = '7777'
# Receiver details.
RECEIVER_IP = '192.168.10.30'
DEFAULT_SURROUND_VOLUME = -20
DEFAULT_MUSIC_VOLUME = -25
VOLUME_UNIT = 3
DEFAULT_INPUT = 'HDMI3'

# Prepare logger.
logbook.StreamHandler(sys.stdout).push_application()
log = logbook.Logger('ControlServer')


def main():
    """
    Run forever and perform TV related commands using the CEC-Client.
    """
    log.info('Initializing connections...')
    # Define receiver.
    receiver = rxv.RXV('http://{}:80/YamahaRemoteControl/ctrl'.format(RECEIVER_IP), 'RX-V671')
    # Define TV server socket.
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind('tcp://*:{}'.format(PORT))
    # Define sound sever socket.
    context = zmq.Context()
    media_server_socket = context.socket(zmq.PAIR)
    media_server_socket.connect('tcp://{}:{}'.format(MEDIA_SERVER_IP, MEDIA_SERVER_PORT))
    # Start listening!
    while True:
        log.info('Waiting for a new command...')
        message = socket.recv_string()
        try:
            if message == 'TV_ON':
                # Turn the TV on.
                log.info('Turning the TV on!')
                os.system('echo "on 0" | cec-client -s')
            elif message == 'TV_OFF':
                # Turn the TV off.
                log.info('Turning the TV off!')
                os.system('echo "standby 0" | cec-client -s')
            elif message == 'RECEIVER_ON_SURROUND':
                # Turn the receiver on.
                log.info('Turning the receiver on surround mode!')
                if not receiver.on:
                    receiver.on = True
                # Set input.
                if receiver.input != DEFAULT_INPUT:
                    receiver.input = DEFAULT_INPUT
                # Set Surround.
                request_text = '<Surround><Program_Sel><Current><Straight>Off</Straight><Sound_Program>Surround Decoder' \
                               '</Sound_Program></Current></Program_Sel></Surround>'
                receiver._request('PUT', request_text)
                # Set volume.
                if receiver.volume != DEFAULT_SURROUND_VOLUME:
                    receiver.volume = DEFAULT_SURROUND_VOLUME
                # Set sound output to receiver using the media server.
                media_server_socket.send_string('SOUND_RECEIVER')
            elif message == 'RECEIVER_ON_MUSIC':
                # Turn the receiver on.
                log.info('Turning the receiver on music mode!')
                if not receiver.on:
                    receiver.on = True
                # Set input.
                if receiver.input != DEFAULT_INPUT:
                    receiver.input = DEFAULT_INPUT
                # Set Surround.
                request_text = '<Surround><Program_Sel><Current><Sound_Program>7ch Stereo</Sound_Program>' \
                               '</Current></Program_Sel></Surround>'
                receiver._request('PUT', request_text)
                # Set volume.
                if receiver.volume != DEFAULT_MUSIC_VOLUME:
                    receiver.volume = DEFAULT_MUSIC_VOLUME
                # Set sound output to receiver using the media server.
                media_server_socket.send_string('SOUND_RECEIVER')
            elif message == 'RECEIVER_TURN_UP':
                # Turn receiver volume up.
                log.info('Turning receiver volume up!')
                if receiver.on:
                    receiver.volume += VOLUME_UNIT
            elif message == 'RECEIVER_TURN_DOWN':
                # Turn receiver volume down.
                log.info('Turning receiver volume down!')
                if receiver.on:
                    receiver.volume -= VOLUME_UNIT
            elif message == 'RECEIVER_OFF':
                # Turn the receiver off.
                log.info('Turning the receiver off!')
                if receiver.on:
                    receiver.on = False
                # Set sound output to computer using the media server.
                media_server_socket.send_string('SOUND_COMPUTER')
            elif message == 'SOUND_RECEIVER':
                # Set sound output to receiver using the media server.
                log.info('Setting sound output to receiver!')
                media_server_socket.send_string('SOUND_RECEIVER')
            elif message == 'SOUND_COMPUTER':
                # Set sound output to computer using the media server.
                log.info('Setting sound output to computer!')
                media_server_socket.send_string('SOUND_COMPUTER')
            elif message.startswith('YOUTUBE_PLAY_') or message in [
                    'YOUTUBE_STOP', 'YOUTUBE_PREVIOUS', 'YOUTUBE_NEXT', 'YOUTUBE_PAUSE']:
                # Play YouTube in a dedicated browser using the media server.
                media_server_socket.send_string(message)
            elif message.startswith('VIDEO_PLAY_') or message == 'VIDEO_STOP':
                # Play video in a dedicated process using the media server.
                media_server_socket.send_string(message)
            else:
                # Ignore the command.
                log.info('Got a weird command: {}. Moving on...'.format(message))
        except Exception:
            log.exception('Bad error!')


if __name__ == '__main__':
    main()
