from app import app

from flask import jsonify

import logging

LOG = logging.getLogger(__name__)


@app.route('/system/ping')
def ping():
    return jsonify('pong')

