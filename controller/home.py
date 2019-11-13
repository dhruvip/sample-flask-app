from flask import Blueprint, jsonify

home_controller = Blueprint('home', __name__,)

@home_controller.route('/healthcheck')
def status():
    res = {
        'status': 'success',
        'message': 'Instance is healthy'
    }
    return jsonify(res)
