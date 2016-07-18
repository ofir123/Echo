import os
import sys

import logbook
import zmq

PORT = '6666'

# Prepare logger.
logbook.StreamHandler(sys.stdout).push_application()
log = logbook.Logger('TVServer')


def main():
    """
    Run forever and perform TV related commands using the CEC-Client.
    """
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind('tcp://*:{}'.format(PORT))
    while True:
        log.info('Waiting for a new command...')
        message = socket.recv_string()
        if message == 'ON':
            # Turn the TV on.
            log.info('Turning the TV on!')
            os.system('echo "on 0" | cec-client -s')
        elif message == 'OFF':
            # Turn the TV off.
            log.info('Turning the TV off!')
            os.system('echo "standby 0" | cec-client -s')
        else:
            # Ignore the command.
            log.info('Got a weird command: {}. Moving on...'.format(message))


if __name__ == '__main__':
    main()
