from flask import Blueprint, jsonify
from flask import current_app as app

home_controller = Blueprint('home', __name__,)

@home_controller.route('/healthcheck')
def status():
    res = {
        'status': 'success',
        'message': 'Instance is healthy'
    }
    return jsonify(res)

@home_controller.route('check_config')
def check_config():
    return jsonify(app.app_config)
