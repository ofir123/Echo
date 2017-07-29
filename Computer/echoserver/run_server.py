import os
import sys

import click
import logbook
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, FallbackHandler
from tornado.wsgi import WSGIContainer

from echoserver import config
from echoserver.app import app

logger = logbook.Logger(__name__)


def run_server(ip, port):
    flask_container = WSGIContainer(app)
    # SSL.
    settings = {
        'ssl_options': {
            'certfile': os.path.join(os.path.dirname(__file__), 'certs', 'echo-server.cert'),
            'keyfile': os.path.join(os.path.dirname(__file__), 'certs', 'echo-server.key')
        }
    }
    # Tornado wrapper.
    handlers = [
        (r'.*', FallbackHandler, dict(fallback=flask_container))
    ]
    http_server = HTTPServer(Application(handlers), **settings)
    http_server.listen(port, ip)
    IOLoop.instance().start()


@click.command()
@click.option('--ip', default=config.IP)
@click.option('--port', default=config.PORT)
def main(ip, port):
    logger_setup = logbook.NestedSetup([
        logbook.StreamHandler(sys.stdout, level=logbook.INFO, bubble=True),
        logbook.RotatingFileHandler(config.LOG_FILE_PATH, level=logbook.DEBUG, max_size=5 * 1024 * 1024, bubble=True)
    ])
    with logger_setup.applicationbound():
        run_server(ip, port)


if __name__ == '__main__':
    # Fix stdout and stderr issues in case of pythonw.
    if sys.executable.endswith("pythonw.exe"):
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
    main()
