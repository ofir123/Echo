import subprocess

import rxv
from rxv.exceptions import ResponseException

# Raspberry Pi details.
PI_IP = '192.168.10.32'
PI_PORT = '6666'
# Receiver details.
RECEIVER_IP = '192.168.10.30'
# Receiver audio constants.
NIRCMD_PATH = r'c:\Program Files\NirCMD\nircmd.exe'
COMPUTER_DEVICE = 'Speakers'


def main():
	# TV part.
	context = zmq.Context()
	socket = context.socket(zmq.PAIR)
	socket.connect('tcp://{}:{}'.format(PI_IP, PI_PORT))
	socket.send_string('OFF')
	# Set audio output to receiver.
	subprocess.check_output('{} setdefaultsounddevice {}'.format(NIRCMD_PATH, COMPUTER_DEVICE))
	subprocess.check_output('{} setdefaultsounddevice {} 2'.format(NIRCMD_PATH, COMPUTER_DEVICE))
	r = rxv.RXV('http://{}:80/YamahaRemoteControl/ctrl'.format(RECEIVER_IP), 'RX-V671')
	# Turn off.
	if r.on:
		r.off()
	# Success!
	print('Great Success!')
		
		
if __name__ == '__main__':
	main()
