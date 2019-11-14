from flask import Blueprint, jsonify, request
from common import ConnectorFactory
import logging
movie_controller = Blueprint('movies', __name__,)

logger = logging.getLogger('sample-flask-app')

def generate_data_response(data, status_code):
    return {
        'statusCode': str(status_code),
        'data': data,
        'count': len(data)                                                                                                                                                                                                             
    }

def generate_response(message, status_code):
    return {
        'statusCode': str(status_code),
        'message': message                                                                                                                                                                                                           
    }

def generate_error(err_msg, status_code):
    return {
        'statusCode': str(status_code),
        'errorMessage': err_msg
    }
@movie_controller.route('/read_all')
def read_movies_table():
    conn_fac = ConnectorFactory()
    db_conn = conn_fac.make_db_connector()
    qry = '''
    select * from movies order by movie_id desc
    '''
    logger.debug('querying db for all movies')
    res = db_conn.select(qry)

    return jsonify(generate_data_response(res,200))

@movie_controller.route('/search')
def paginated_read():
    payload = {
        'page': request.args.get('page'),
        'limit': request.args.get('limit'),
        'name':  request.args.get('name'),
        'director': request.args.get('director')
    }
    payload = {k:v for k,v in payload.items() if v is not None}

    qry = "select * from movies "

    if all (k in payload for k in ['name','director']):
        qry += "where name like '%{}%' and director like '%{}% ".format(payload['name'],payload['director'])
    elif 'name' in payload:
        qry +="where name like '%{}%' ".format(payload['name'])
    elif 'director' in payload:
        qry +="where director like '%{}%' ".format(payload['director'])
    if 'limit' in payload:
        limit = payload['limit'] if (int(payload['limit']) > 0) else 0
        if limit == 0:
            return jsonify(generate_error('limit should be greated than 0',400))
        qry += "limit {} ".format(limit)
    if all (k in payload for k in ['page','limit']):
        limit = int(payload['limit']) if (int(payload['limit']) > 0) else 0
        page = int(payload['page']) if (int(payload['limit']) > 0) else 1
        offset = limit*(page-1)
        qry += "offset {} ".format(offset)
    logger.debug('query: ' + qry)
    conn_fac = ConnectorFactory()
    db_conn = conn_fac.make_db_connector()
    logger.debug('querying db for paginated movies')
    res = db_conn.select(qry)
    return jsonify(generate_data_response(res,200))

@movie_controller.route('/add_one', methods=['POST'])
def add_new_movie():
    payload = request.get_json()    
    conn_fac = ConnectorFactory()
    db_conn = conn_fac.make_db_connector()
    if not all (k in payload for k in ['name','popularity','director','imdb_score']):
        response = generate_error('POST data must have name, popularity, director and imdb_score',400)
        return jsonify(response)
    else:
        qry = """INSERT INTO `Movies`
                                ('name', 'popularity', 'director', 'imdb_score') 
                                VALUES {}"""
        new_movie = (payload['name'],payload['popularity'],payload['director'],payload['imdb_score'])
        qry = qry.format(new_movie)
        res_code = db_conn.insert(qry)
        if res_code:
            return generate_response('Successfully inserted record.',200)
        else: 
            return generate_error('Database insertion failed',500)


