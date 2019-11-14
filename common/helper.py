
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