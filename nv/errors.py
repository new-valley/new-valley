from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from flask_jwt_extended.exceptions import JWTExtendedException
import jwt
from nv.util import mk_errors
from nv import metaconfig
from flask import current_app

def jwt_error_handler(error):
    code = 401
    if isinstance(error, jwt.exceptions.ExpiredSignatureError):
        messages = ['expired_token']
    else:
        messages = list(getattr(error, 'args', []))
    return mk_errors(code, messages)

def permission_error_handler(error):
    code = 401
    messages = list(getattr(error, 'args', ['permission denied for action']))
    return mk_errors(code, messages)

def http_error_handler(error):
    resp = error.response
    if resp is None:
        code = error.code
        messages = [error.description]
    else:
        code = getattr(resp, 'status_code', 500)
        json = resp.get_json()
        if 'errors' in json and json['errors']:
            messages = [e['message'] for e in json['errors'] if 'message' in e]
        else:
            messages = [str(resp.status)]
    return mk_errors(code, messages)

def validation_error_handler(error):
    code = getattr(error, 'status_code', 500)
    messages = getattr(error, 'messages', [])
    return mk_errors(code, messages)

def generic_error_handler(error):
    code = getattr(error, 'status_code', 500)
    if current_app.config['DEBUG']:
        messages = [str(error)]
    else:
        messages = ['something went wrong!']
    return mk_errors(code, messages)

def error_handler(error):
    try:
        if isinstance(error, (JWTExtendedException, jwt.exceptions.PyJWTError)):
            return jwt_error_handler(error)
        elif isinstance(error, HTTPException):
            return http_error_handler(error)
        elif isinstance(error, ValidationError):
            return validation_error_handler(error)
        elif isinstance(error, PermissionError):
            return permission_error_handler(error)
        else:
            return generic_error_handler(error)
    except:
        return mk_errors(500, 'something went wrong!')

def register_handlers(app):
    app.errorhandler(Exception)(error_handler)
    app.errorhandler(HTTPException)(error_handler)
    app.handle_user_exception = error_handler
