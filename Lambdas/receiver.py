import ssl
import urllib.request

ECHO_SERVER_HOST = 'casagabirol.hopto.org'
ECHO_SERVER_PORT = '9999'
ECHO_SERVER_URL = 'https://{}:{}/api'.format(ECHO_SERVER_HOST, ECHO_SERVER_PORT)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def _get_request(api_path):
    urllib.request.urlopen(ECHO_SERVER_URL + api_path, context=ctx).read()


def lambda_handler(request, context):
    header = request['header']
    if header['namespace'] == 'Alexa.Discovery' and header['name'] == 'Discover':
        return handle_discovery(request, context)

    elif header['namespace'] == 'Alexa.PowerController':
        return handle_power_controller(request, context)


def handle_discovery(request, context):
    header = request['header']
    header['name'] = 'Discover.Response'
    payload = {
        "endpoints": [
            {
                "endpointId": "receiver",
                "friendlyName": "Receiver",
                "description": "Smart Receiver by Yamaha",
                "manufacturerName": "Yamaha",
                "displayCategories": [],
                "capabilities": [
                    {
                        "type": "AlexaInterface",
                        "interface": "Alexa.PowerController",
                        "version": "1.0",
                        "properties": {

                        }
                    }
                ]
            }
        ]
    }
    return {
        'header': header,
        'payload': payload
    }


def handle_power_controller(request, context):
    header = request['header']
    receiver_command = 'TurnOn' if header['name'] == 'on' else 'off'
    _get_request('/receiver/{}'.format(receiver_command))
    header['name'] = 'Response'
    return {
        'header': header,
        'payload': {}
    }
