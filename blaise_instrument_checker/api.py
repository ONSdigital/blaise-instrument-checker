import logging
import os
import sys
import pyblaise
from flask import Flask, jsonify, request, g
from flask.logging import default_handler
# import logging
# from pythonjsonlogger import jsonlogger
import json_logging

app = Flask(__name__)

json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)

# init the logger as usual
logger = logging.getLogger("test-logger")
logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler(sys.stdout))
# handler.setFormatter(logger_format2)
app.logger.addHandler(logging.StreamHandler(sys.stdout))


# class CustomJsonFormatter(jsonlogger.JsonFormatter):
#     def add_fields(self, log_record, record, message_dict):
#         super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
#         if not log_record.get('timestamp'):
#             record2 = record
#             # this doesn't use record.created, so it is slightly off
#             # now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
#             log_record['timestamp'] = record.asctime
#         if log_record.get('level'):
#             log_record['severity'] = log_record['level'].upper()
#         else:
#             log_record['severity'] = record.levelname




# logging_format = CustomJsonFormatter(
#     '(timestamp) (severity) (name) (message)'
# )

logger_format2 = logging.Formatter(
    '{"timestamp": "%(asctime)s", "service": "blaise_instrument_checker",  "severity": "%(levelname)s", "module": "%(module)s" "message": "%(message)s"}'
)
#
# logging.basicConfig(level=logging.DEBUG)
app.logger.removeHandler(default_handler)
# app.logger.setFormatter(logger_format)

#
#
# app.logger.setLevel(os.getenv("LOG_LEVEL", "WARN"))
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(os.getenv("LOG_LEVEL", "WARN"))
# handler.setFormatter(logger_format2)
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

    app.logger.info("Hello")
    app.logger.info(f"Host : {host}")
    app.logger.info(f"Instrument to check : {instrument_check} ")
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
    correlation_id = json_logging.get_correlation_id()
    return jsonify("Not found"), 404
