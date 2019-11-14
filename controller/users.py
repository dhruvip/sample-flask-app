from flask import Blueprint, jsonify, request
from common import ConnectorFactory,generate_data_response, \
    generate_error, generate_response
import logging

user_controller = Blueprint('users', __name__,)
logger = logging.getLogger('sample-flask-app')


@user_controller.route('/read_all')
def read_users_table():
    conn_fac = ConnectorFactory()
    db_conn = conn_fac.make_db_connector()
    qry = '''
    select * from users order by user_id desc
    '''
    logger.debug('querying db for all users')
    res = db_conn.select(qry)

    return jsonify(generate_data_response(res,200))

@user_controller.route('/add_one', methods=['POST'])
def add_new_user():
    payload = request.get_json()    
    conn_fac = ConnectorFactory()
    db_conn = conn_fac.make_db_connector()
    if not all (k in payload for k in ['name','email']):
        response = generate_error('POST data must have name and email',400)
        return jsonify(response)
    else:
        qry = """INSERT INTO `Users`
                                ('name', 'email', 'isadmin') 
                                VALUES {}"""
        new_user = (payload['name'],payload['email'],(payload['isadmin'] if 'isadmin' in payload else 0))
        qry = qry.format(new_user)
        res_code = db_conn.insert(qry)
        if res_code:
            return generate_response('Successfully inserted record.',200)
        else: 
            return generate_error('Database insertion failed',500)

@user_controller.route('update_one', methods=['POST'])
def update_user():
    payload = request.get_json()    
    if not ('user_id' in payload):
        response = generate_error('User ID required for update',400)
        return jsonify(response)

    conn_fac = ConnectorFactory()
    db_conn = conn_fac.make_db_connector()
    qry = "update users set "
    update_list = list()
    if 'name' in payload:
        update_list.append(str('name') + "='" + str(payload['name']) +"'")
    if 'email' in payload:
        update_list.append(str('email') + "='" + str(payload['email']) +"'")  
    if 'isadmin' in payload:      
        update_list.append(str('isadmin') + "=" + str(payload['isadmin']))
    qry = qry +  ', '.join(k for k in update_list)
    qry += " where user_id={}".format(int(payload['user_id']))
    res_code = db_conn.update(qry)
    if res_code:
        return generate_response('Successfully updated record.',200)
    else: 
        return generate_error('Database record update failed',500)


@user_controller.route('/search')
def paginated_read():
    payload = {
        'page': request.args.get('page'),
        'limit': request.args.get('limit'),
        'name':  request.args.get('name'),
        'email': request.args.get('email'),
        'isadmin': request.args.get('isadmin'),
        'user_id': request.args.get('user_id')
    }
    payload = {k:v for k,v in payload.items() if v is not None}

    qry = "select * from users "
    where_list = list()
    if 'user_id' in payload:
        q = " user_id={} ".format(payload['user_id'])
        where_list.append(q)
    if 'name' in payload:
        q= " name like '%{}%' ".format(payload['name'])
        where_list.append(q)
    if 'email' in payload:
        q =" email like '%{}%' ".format(payload['email'])
        where_list.append(q)
    if 'isadmin' in payload:
        q =" isadmin={} ".format(payload['isadmin'])
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
    logger.debug('querying db for paginated users')
    res = db_conn.select(qry)
    return jsonify(generate_data_response(res,200))
