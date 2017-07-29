from flask import Flask

from echoserver import config
from echoserver.views import app_views

app = Flask(__name__.split('.')[0])

app.register_blueprint(app_views, url_prefix='/api')

if __name__ == '__main__':
    app.run(config.IP, config.PORT)
