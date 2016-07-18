import subprocess

import rxv
from rxv.exceptions import ResponseException
import zmq

# Raspberry Pi details.
PI_IP = '192.168.10.32'
PI_PORT = '6666'
# Receiver details.
RECEIVER_IP = '192.168.10.30'
DEFAULT_VOLUME = -20
DEFAULT_INPUT = 'HDMI5'
# Receiver audio constants.
NIRCMD_PATH = r'c:\Program Files\NirCMD\nircmd.exe'
RECEIVER_DEVICE = 'SAMSUNG-4'


def main():
	# TV part.
	context = zmq.Context()
	socket = context.socket(zmq.PAIR)
	socket.connect('tcp://{}:{}'.format(PI_IP, PI_PORT))
	socket.send_string('ON')
	# Receiver part.
	r = rxv.RXV('http://{}:80/YamahaRemoteControl/ctrl'.format(RECEIVER_IP), 'RX-V671')
	# Turn on.
	if not r.on:
		r.on = True
	# Set input.
	if r.input != DEFAULT_INPUT:
		r.input = DEFAULT_INPUT
	# Set Surround.
	request_text = '<Surround><Program_Sel><Current><Straight>Off</Straight><Sound_Program>Surround Decoder</Sound_Program></Current></Program_Sel></Surround>'
	r._request('PUT', request_text)
	# Set volume.
	if r.volume != DEFAULT_VOLUME:
		r.volume = DEFAULT_VOLUME
	# Set audio output to receiver.
	subprocess.check_output('{} setdefaultsounddevice {}'.format(NIRCMD_PATH, RECEIVER_DEVICE))
	subprocess.check_output('{} setdefaultsounddevice {} 2'.format(NIRCMD_PATH, RECEIVER_DEVICE))
	# Success!
	print('Great Success!')
		
		
if __name__ == '__main__':
	main()
