import os

import pyblaise
from flask import Flask, jsonify, request, g

app = Flask(__name__)

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


@app.route('/api/instruments', methods=["GET"])
def get_all_instruments_on_blaise():
    BLAISE_HOST = request.args.get('vm_name', None, type=str)

    app.logger.info(f"BLAISE_HOST : {BLAISE_HOST}")
    app.logger.info(f"PROTOCOL : {PROTOCOL}")
    app.logger.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, BLAISE_HOST, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        app.logger.debug(f"get_auth_token Status: {status}")
        if status != 200:
            return jsonify({"status": "error", "message": f"Could not get authentication token from blaise on '{PROTOCOL}://{BLAISE_HOST}' as '{BLAISE_USERNAME}'"}), 401
    except Exception as e:
        app.logger.exception(f"Could not get authentication token from blaise on '{PROTOCOL}://{BLAISE_HOST}' as '{BLAISE_USERNAME}'")
        return jsonify({"status": "error", "message": f"Could not get authentication token from blaise on '{PROTOCOL}://{BLAISE_HOST}' as '{BLAISE_USERNAME}'"}), 401

    try:
        status, instruments = pyblaise.get_list_of_instruments(PROTOCOL, BLAISE_HOST, 8031, token)
        app.logger.info(f"get_list_of_instruments status: {status}")
        if status != 200:
            return jsonify({"status": "error", "message": f"get list of instruments on '{PROTOCOL}://{BLAISE_HOST}' as '{BLAISE_USERNAME}' failed"}), status
        return jsonify(instruments), 200
    except Exception as e:
        app.logger.exception(f"get list of instruments on '{PROTOCOL}://{BLAISE_HOST}' as '{BLAISE_USERNAME}' failed'")
        return jsonify({"status": "error", "message": f"get list of instruments on '{PROTOCOL}://{BLAISE_HOST}' as '{BLAISE_USERNAME}' failed"}), status
