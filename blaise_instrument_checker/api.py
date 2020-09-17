import logging
import os
import sys
import pyblaise
from flask import Flask, jsonify, request, g
from flask.logging import default_handler
# import logging


app = Flask(__name__)


# app.logger_format = app.loggerging.Formatter(
#     '{"timestamp": "%(asctime)s", "service": "blaise_instrument_checker",  "severity": "%(levelname)s", "module": "%(module)s" "message": "%(message)s"}'
# )
#
# app.logger.basicConfig(level=app.logger.DEBUG)
# app.app.loggerger.removeHandler(default_handler)
# default_handler.setFormatter(app.logger_format)
#
#
# # app.app.loggerger.setLevel(os.getenv("app.logger_LEVEL", "WARN"))
# handler = app.loggerging.StreamHandler(sys.stdout)
# handler.setLevel(os.getenv("app.logger_LEVEL", "WARN"))
# handler.setFormatter(app.logger_format)
# app.app.loggerger.addHandler(handler)

PROTOCOL = os.getenv("PROTOCOL", None)
BLAISE_USERNAME = os.getenv("BLAISE_USERNAME", None)
BLAISE_PASSWORD = os.getenv("BLAISE_PASSWORD", None)


@app.route('/')
def health_check():
    app.app.loggerger.debug(f"health_check from {request.remote_addr}")
    return ":)", 200


@app.route('/instrument')
def check_instrument_on_blaise():
    host = request.args.get('vm_name', None, type=str)
    instrument_check = request.args.get('instrument', None, type=str)

    app.logger.info("Hello")
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

    app.logger.exception(f"could find instrument '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
    return jsonify("Not found"), 404
