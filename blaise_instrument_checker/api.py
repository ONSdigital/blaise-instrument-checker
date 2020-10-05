import os
import sys
import logging
from flask import Flask, jsonify, request
import pyblaise
from werkzeug import secure_filename

app = Flask(__name__)

app.logger.setLevel(os.getenv("LOG_LEVEL", "WARN"))
handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(os.getenv("LOG_LEVEL", "WARN"))
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


@app.route('/instruments')
def get_all_instruments_on_blaise():
    host = request.args.get('vm_name', None, type=str)
    # instrument_check = request.args.get('instrument', None, type=str)

    app.logger.info(f"Host : {host}")

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
        return jsonify(instruments), 200
    except Exception as e:
        app.logger.exception(f"could not get list of instruments from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500


@app.route('/users')
def get_all_users_on_blaise():
    host = request.args.get('vm_name', None, type=str)
    # instrument_check = request.args.get('instrument', None, type=str)

    app.logger.info(f"Host : {host}")

    app.logger.info(f"PROTOCOL : {PROTOCOL}")
    app.logger.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, host, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        app.logger.debug(f"get_auth_token Status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get authentication token from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    try:
        status, instruments = pyblaise.get_all_users(PROTOCOL, host, 8031, token)
        app.logger.info(f"get_all_users_on_blaise status: {status}")
        return jsonify(instruments), 200
    except Exception as e:
        app.logger.exception(f"could not get list of users from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500


@app.route('/upload_survey', methods=["POST"])
def upload_survey_blaise():
    f = request.files['survey_file']
    f.save(secure_filename(f.filename))

    server_park = request.args.get('server_park', None, type=str)
    host = request.args.get('vm_name', None, type=str)
    survey_name = request.args.get('instrument', None, type=str)
    survey_ID = pyblaise.get_manifest_id_from_zip("./" + f.filename)

    app.logger.info(f"Host : {host}")
    app.logger.info(f"PROTOCOL : {PROTOCOL}")
    app.logger.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, host, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        app.logger.debug(f"get_auth_token Status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get authentication token from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    try:
        app.logger.info(f"Uploading survey {survey_name} to {server_park} server park")
        status = pyblaise.upload_survey(PROTOCOL, host, 8031, server_park, survey_name, survey_ID, token, "./" + f.filename)
        app.logger.info(f"Uploaded survey status: {status}")
        return jsonify(status), 200
    except Exception as e:
        app.logger.exception(f"could not upload survey {survey_name} from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500
