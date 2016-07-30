Echo
====================

A collection of Python scripts for Amazon Echo, in order to make every house super smart and generally awesome!

Ingredients
====================
* Amazon Echo (to control everything with your voice)
* A server (for the sound output and browser control scripts)
* Raspberry pi 3 (for TV control through CEC)
* Yamaha RX-V Receiver (for the Receiver control scripts)
* LIFX bulbs (for the cool lighting effects)

Scripts
====================
* media_server.py - Runs on the server controls sound output and browser.
* control_server.py - Runs on the Raspberry Pi (which is connected to the TV through HDMI), and listens for commands.
* computer.py - Turns on the TV and the receiver, switches the receiver to the computer's channel and sets the sound settings in both the receiver and the computer.
* music.py - Same as computer.py, but with different sound settings for the receiver.
* off.py - Turns everything off (not working with the current TV since LG sucks and doesn't support CEC standby).

Intents
====================
youtube_intent.py - A Lambda function controlling YouTube.
receiver_intent.py - A Lambda function controlling the receiver.
tv_intent.py - A Lambda function controlling TV.
