import pyblaise
import os
from flask import Flask, jsonify, request
import dateutil.parser
import logging
from .util.service_logging import log
# log = logging.getLogger(__name__)

app = Flask(__name__)

PROTOCOL = os.getenv("PROTOCOL", None)
BLAISE_USERNAME = os.getenv("BLAISE_USERNAME", None)
BLAISE_PASSWORD = os.getenv("BLAISE_PASSWORD", None)


@app.route('/')
def health_check():
    return ":)", 200


@app.route('/instrument')
def check_instrument_on_blaise():
    host = request.args.get('vm_name', None, type=str)
    instrument_check = request.args.get('instrument', None, type=str)

    log.info(f"Host : {host}")
    log.info(f"Instrument to check : {instrument_check}")
    log.info(f"PROTOCOL : {PROTOCOL}")
    log.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")
    log.info(f"BLAISE_PASSWORD : {BLAISE_PASSWORD}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, host, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        log.info(f"get_auth_token Status: {status}")
        status, instruments = pyblaise.get_list_of_instruments(PROTOCOL, host, 8031, token)
        log.info(f"get_list_of_instruments status: {status}")
        for instrument in instruments:
            if instrument['name'] == instrument_check:
                log.info(f"Found {instrument_check}")
                date = dateutil.parser.parse(instrument['install-date'])
                date_string = date.strftime("%H:%M %d/%m/%Y")
                return jsonify(date_string)
        return jsonify("Not found"), 404
    except TypeError as ex:
        log.error(f"get_list_of_instruments failed")
    return jsonify("false"), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0')
