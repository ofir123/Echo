import subprocess

import rxv
from rxv.exceptions import ResponseException

# Receiver details.
RECEIVER_IP = '192.168.10.30'
DEFAULT_VOLUME = -20
DEFAULT_INPUT = 'HDMI3'
# Receiver audio constants.
NIRCMD_PATH = r'c:\Program Files\NirCMD\nircmd.exe'
RECEIVER_DEVICE = 'SAMSUNG-4'


def main():
	r = rxv.RXV('http://{}:80/YamahaRemoteControl/ctrl'.format(RECEIVER_IP), 'RX-V671')
	# Turn on.
	if not r.on:
		r.on = True
	# Set input.
	if r.input != DEFAULT_INPUT:
		r.input = DEFAULT_INPUT
	# Set 7-channel stereo.
	request_text = '<Surround><Program_Sel><Current><Sound_Program>7ch Stereo</Sound_Program></Current></Program_Sel></Surround>'
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
