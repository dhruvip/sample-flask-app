from flask import Flask, g, jsonify
import logging
import os
import json
from flask_cors import CORS
from controller import home_controller

app = Flask(__name__)

env_type = os.environ.get('API_APP_ENV','dev')
print('using environment : {}'.format(env_type))
CONFIG_FILE_PATH = './config/{}.json'.format(env_type)
print('Config path : {}'.format(CONFIG_FILE_PATH))
CONFIG = json.load(open(CONFIG_FILE_PATH))

logging.debug('Registering the routes: ')
app.register_blueprint(home_controller)

if __name__ == '__main__':
    app.app_config = CONFIG
    app.run(host=CONFIG['web_server']['host'],
            port=CONFIG['web_server']['port'],
            debug=CONFIG['web_server']['debug'])