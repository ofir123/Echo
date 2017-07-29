EchoServer
====================

A simple Flask server which communicates with Amazon Echo, in order to make every house super smart and generally awesome!

Ingredients
====================
* Amazon Echo (to control everything with your voice)
* A server (for the sound output and browser control scripts)
* Raspberry pi 3 (for TV control through CEC)
* Yamaha RX-V Receiver (for the Receiver control scripts)
* LIFX bulbs (for the cool lighting effects)

Setup
====================
Just go to the `Computer` directory, and run: 
```
python setup.py develop
python echoserver/run_server.py
```
To get the server going on your computer.

Then, do the same with the `RaspberryPi` directory on your RaspberryPi device.

Intents
====================
youtube_intent.py - A Lambda function controlling YouTube.
receiver_intent.py - A Lambda function controlling the receiver.
tv_intent.py - A Lambda function controlling TV.
