import os
import time

import pyblaise
from flask import Flask, jsonify, request, g
from google.cloud import logging as gcplogging
from werkzeug.wrappers import Request

# app = Flask(__name__)

client = gcplogging.Client()

import logging
from logging.config import dictConfig


# curl -v  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36" -H "X-Cloud-Trace-Context: `python -c "impo uuid; print uuid.uuid4()"`" http://localhost:8080/


class GCPHandler(logging.Handler):
    def __init__(self, logName):
        self.logName = logName
        self.logger = client.logger(logName)
        logging.Handler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        TEXT = msg
        DEFAULT_LABELS = {'foo': 'spam'}
        LABELS = {'foo': 'bar', 'baz': 'qux'}
        SEVERITY = 'INFO'
        TRACE = "projects/{}/traces/{}".format(client.project, request.headers.get('X-Cloud-Trace-Context'))
        self.logger.log_text(TEXT, client=client, labels=LABELS, severity=SEVERITY, trace=TRACE)


class LoggerConfig:
    dictConfig = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {'format': '%(asctime)s - %(name)s - %(levelname)s - '
                                   '%(message)s - [in %(pathname)s:%(lineno)d]'},
            'short': {'format': '%(message)s'}
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'app.log',
                'maxBytes': 5000000,
                'backupCount': 10
            },
            'gcp': {
                'level': 'INFO',
                'formatter': 'short',
                'class': 'main.GCPHandler',
                'logName': 'child'
            },
            'debug': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.StreamHandler'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO'
            },
        },
        'loggers': {
            'child': {
                'handlers': ['gcp'],
                'level': 'DEBUG',
                'propagate': True},
        },
        # 'root': { 'level': 'DEBUG', 'handlers': ['console'] }
    }


logging.config.dictConfig(LoggerConfig.dictConfig)


class TransitMiddleWare(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ, shallow=True)
        host = req.headers.get('Host')
        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = TransitMiddleWare(app.wsgi_app)

parent_logger = client.logger("parent")
logger = logging.getLogger("child")


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


@app.after_request
def add_logger(response):
    TEXT = u'TEXT'
    DEFAULT_LABELS = {'foo': 'spam'}
    LABELS = {'foo': 'bar', 'baz': 'qux'}
    SEVERITY = 'INFO'
    TRACE = "projects/{}/traces/{}".format(client.project, request.headers.get('X-Cloud-Trace-Context'))

    REQUEST = {
        'requestMethod': request.method,
        'requestUrl': request.url,
        'status': response.status_code,
        'userAgent': request.headers.get('USER-AGENT'),
        'responseSize': response.content_length,
        'latency': g.request_time(),
        'remoteIp': request.remote_addr
    }

    parent_logger.log_text(TEXT, client=client, labels=LABELS, severity=SEVERITY, http_request=REQUEST, trace=TRACE)

    # optional...similar to envoy: transmit response time back to the user
    response.headers['x-upstream-service-time'] = g.request_time()

    return response


# app.logger.setLevel(os.getenv("LOG_LEVEL", "WARN"))
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(os.getenv("LOG_LEVEL", "WARN"))
# app.logger.addHandler(handler)

PROTOCOL = os.getenv("PROTOCOL", None)
BLAISE_USERNAME = os.getenv("BLAISE_USERNAME", None)
BLAISE_PASSWORD = os.getenv("BLAISE_PASSWORD", None)


@app.route('/')
def health_check():
    app.logger.debug(f"health_check from {request.remote_addr}")
    return ":)", 200


@app.route('/instrument')
def check_instrument_on_blaise():
    host = request.args.get('vm_name', None, type=str)
    instrument_check = request.args.get('instrument', None, type=str)

    app.logger.info(f"Host : {host}")
    app.logger.info(f"Instrument to check : {instrument_check}")
    app.logger.info(f"PROTOCOL : {PROTOCOL}")
    app.logger.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, host, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        app.logger.debug(f"get_auth_token Status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get authentication token from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    try:
        status, instruments = pyblaise.get_list_of_instruments(PROTOCOL, host, 8031, token)
        app.logger.info(f"get_list_of_instruments status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get list of instruments from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    for instrument in instruments:
        if instrument['name'] == instrument_check:
            app.logger.info(f"Found {instrument_check}")
            return jsonify(instrument)

    return jsonify("Not found"), 404
