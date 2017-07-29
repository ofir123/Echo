import zmq

# Raspberry Pi details.
PI_IP = '192.168.10.32'
PI_PORT = '6666'


def main():
    # Raspberry Pi part.
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect('tcp://{}:{}'.format(PI_IP, PI_PORT))
    # TV part.
    socket.send_string('TV_OFF')
    # Receiver part.
    socket.send_string('RECEIVER_OFF')
    # Set audio output to computer.
    socket.send_string('SOUND_COMPUTER')
    # Success!
    print('Great Success!')


if __name__ == '__main__':
    main()
