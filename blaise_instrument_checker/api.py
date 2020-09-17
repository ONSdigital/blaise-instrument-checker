import logging
import os
import sys

import pyblaise
from flask import Flask, jsonify, request, g
from flask.logging import default_handler
import logging


app = Flask(__name__)


log_format = logging.Formatter(
    '{"timestamp": "%(asctime)s", "service": "blaise_instrument_checker",  "severity": "%(levelname)s", "module": "%(module)s" "message": "%(message)s"}'
)

logging.basicConfig(level=logging.DEBUG)
# app.logger.removeHandler(default_handler)
# default_handler.setFormatter(log_format)
#
#
# # app.logger.setLevel(os.getenv("LOG_LEVEL", "WARN"))
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(os.getenv("LOG_LEVEL", "WARN"))
# handler.setFormatter(log_format)
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

    logging.info("Hello")
    logging.info(f"Host : {host}")
    logging.info(f"Instrument to check : {instrument_check}")
    logging.info(f"PROTOCOL : {PROTOCOL}")
    logging.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, host, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        logging.debug(f"get_auth_token Status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get authentication token from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    try:
        status, instruments = pyblaise.get_list_of_instruments(PROTOCOL, host, 8031, token)
        logging.info(f"get_list_of_instruments status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get list of instruments from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    for instrument in instruments:
        if instrument['name'] == instrument_check:
            logging.info(f"Found {instrument_check}")
            return jsonify(instrument)

    logging.exception(f"could find instrument '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
    return jsonify("Not found"), 404
