from flask import Blueprint, jsonify, request
from common import ConnectorFactory,generate_data_response, \
    generate_error, generate_response
import logging
movie_controller = Blueprint('movies', __name__,)

logger = logging.getLogger('sample-flask-app')


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
        'director': request.args.get('director'),
        'movie_id': request.args.get('movie_id'),
        'imdb_score':request.args.get('imdb_score')
    }
    payload = {k:v for k,v in payload.items() if v is not None}

    qry = "select * from movies "
    where_list = list()
    if 'movie_id' in payload:
        q = " movie_id={} ".format(payload['movie_id'])
        where_list.append(q)
    if 'name' in payload:
        q= " name like '%{}%' ".format(payload['name'])
        where_list.append(q)
    if 'director' in payload:
        q =" director like '%{}%' ".format(payload['director'])
        where_list.append(q)
    if 'imdb_score' in payload:
        q =" imdb_score={} ".format(payload['imdb_score'])
        where_list.append(q)
    if len(where_list) > 1:
        where_list = 'and'.join(k for k in where_list)
        qry = qry + 'where ' + where_list
    elif len(where_list)==1:
        qry = qry + 'where ' + where_list[0]
    
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
    # if not ('user_id' in payload):
    #     response = generate_error('User ID required for update',400)
    #     return jsonify(response)    
    conn_fac = ConnectorFactory()
    db_conn = conn_fac.make_db_connector()
    if not all (k in payload for k in ['name','popularity','director','imdb_score']):
        response = generate_error('POST data must have name, popularity, director and imdb_score',400)
        return jsonify(response)
    else:

        #Check if admin
        # user_qry = '''
        #     select isadmin from users where user_id={}
        # '''.format(payload['user_id'])
        # check_admin = db_conn.select(user_qry)
        # if not check_admin[0][0]:
        #     return jsonify(generate_error('Unauthorized to update!', 401))

        # Insert 
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

@movie_controller.route('update_one', methods=['POST'])
def update_movie():
    payload = request.get_json()
    # if not ('user_id' in payload):
    #     response = generate_error('User ID required for update',400)
    #     return jsonify(response)    
    if not ('movie_id' in payload):
        response = generate_error('Movie ID required for update',400)
        return jsonify(response)

    conn_fac = ConnectorFactory()
    db_conn = conn_fac.make_db_connector()
    #Check if admin
    # user_qry = '''
    #     select isadmin from users where user_id={}
    # '''.format(payload['user_id'])
    # check_admin = db_conn.select(user_qry)
    # if not check_admin[0][0]:
    #     return jsonify(generate_error('Unauthorized to update!', 401))

    # Update 
    conn_fac = ConnectorFactory()
    db_conn = conn_fac.make_db_connector()
    update_qry = "update movies set "
    update_list = list()
    if 'name' in payload:
        update_list.append(str('name') + "='" + str(payload['name']) +"'")
    if 'popularity' in payload:
        update_list.append(str('popularity') + "=" + str(payload['popularity']))  
    if 'director' in payload:      
        update_list.append(str('director') + "='" + str(payload['director'])+"'")
    if 'imdb_score' in payload:      
        update_list.append(str('imdb_score') + "=" + str(payload['imdb_score']))
    update_qry = update_qry +  ', '.join(k for k in update_list)
    update_qry += " where movie_id={}".format(int(payload['movie_id']))
    res_code = db_conn.update(update_qry)
    if res_code:
        return generate_response('Successfully updated record.',200)
    else: 
        return generate_error('Database record update failed',500)
