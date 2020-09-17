import logging
import os
import sys
import pyblaise
from flask import Flask, jsonify, request, g
from flask.logging import default_handler
# import logging
from pythonjsonlogger import jsonlogger



app = Flask(__name__)

logging_format = formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
)

# logger_format = logging.Formatter(
#     '{"timestamp": "%(asctime)s", "service": "blaise_instrument_checker",  "severity": "%(levelname)s", "module": "%(module)s" "message": "%(message)s"}'
# )
#
# logging.basicConfig(level=logging.DEBUG)
app.logger.removeHandler(default_handler)
# app.logger.setFormatter(logger_format)

#
#
app.logger.setLevel(os.getenv("LOG_LEVEL", "WARN"))
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(os.getenv("LOG_LEVEL", "WARN"))
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

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

    app.logger.error(f"could not instrument {instrument_check} on'{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
    return jsonify("Not found"), 404
