from flask import Flask, g, jsonify
import logging
import os
import json
from controller import home_controller, movie_controller,user_controller
import sqlite3
from common import SqlConnector, setup_custom_logger, ConnectorFactory
from werkzeug.contrib.fixers import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

env_type = os.environ.get('API_APP_ENV','dev')
print('using environment : {}'.format(env_type))
CONFIG_FILE_PATH = './config/{}.json'.format(env_type)
print('Config path : {}'.format(CONFIG_FILE_PATH))
CONFIG = json.load(open(CONFIG_FILE_PATH))

logger = setup_custom_logger('sample-flask-app')

logger.debug('Registering the routes: ')
app.register_blueprint(home_controller, url_prefix='/')
app.register_blueprint(movie_controller, url_prefix='/movies')
app.register_blueprint(user_controller, url_prefix='/users')


DATABASE = './config/{}.db'.format(CONFIG['db']['sqlite_path'])

with app.app_context():
    conn_fac = ConnectorFactory(CONFIG)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

SCHEMA_FILE = './config/{}'.format(CONFIG['db']['schema_file'])

@app.route('/initdb')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource(SCHEMA_FILE, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        return jsonify({'message': 'database init successfull'})

@app.route('/seeddb')
def seed_db():
    with app.app_context():
        sqliteConnection = get_db()
        movies_seed = json.load(open('./config/movie_seed.json'))
        movies_seed = list(map(lambda x: (x['name'],x['99popularity'],x['director'],x['imdb_score']),movies_seed))
        movies = ', '.join(str(k) for k in movies_seed)

        user_seed = json.load(open('./config/user_seed.json'))
        user_seed = list(map(lambda x: (x['name'],x['email'],x['isadmin']),user_seed))
        users = ', '.join(str(k) for k in user_seed)

        try:
            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")

            sqlite_insert_query = """INSERT INTO `movies`
                                ('name', 'popularity', 'director', 'imdb_score') 
                                VALUES {}"""
            sqlite_insert_query = sqlite_insert_query.format(movies)
            count = cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()

            sqlite_insert_query = """INSERT INTO `users`
                                ('name', 'email', 'isadmin') 
                                VALUES {}"""
            sqlite_insert_query = sqlite_insert_query.format(users)
            count = cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()            
            print("Record inserted successfully into tables movies and users")
            cursor.close()
            return jsonify({'message':'Successfully Seeded database'})
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
            return jsonify({'message':'Failed to insert data into sqlite table'+str(error)})
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The SQLite connection is closed")

@app.route('/dropdb')
def drop_tables():
    qry = '''
        DROP TABLE IF EXISTS Movies;
        DROP TABLE IF EXISTS Users;
    '''
    with app.app_context():
        db = get_db()
        db.cursor().executescript(qry)
        db.commit()
    return jsonify({'message':'Successfully dropped database'})

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.app_config = CONFIG
    app.run(host=CONFIG['web_server']['host'],
            port=CONFIG['web_server']['port'],
            debug=CONFIG['web_server']['debug'])