from flask import request
from flask_restful import (
    Resource,
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt
)
from webargs.flaskparser import parser
from webargs.fields import (
    Str,
    Int,
)
from webargs import validate
from nv.models import (
    User,
)
from nv.serializers import (
    UserSchema,
)
from nv.util import (
    mk_errors,
)
from nv.resources import common
from nv.database import db
from nv import config

#def check_priviledges():
#    if not get_jwt_identity() in config.superusers:
#        abort(401, 'unauthorized user')

_USER_PASS_ARGS = {
    'username': Str(required=True),
    'password': Str(
        validate=validate.Length(min=config.min_password_len), required=True),
    'email': Str(required=True),
    'roles': Str(),
    'status': Str(),
    'avatar_id': Int(required=True),
    'signature': Str(),
}

class UsersRes(Resource):
    #@jwt_required
    def get(self):
        args = common.parse_get_coll_args(request)
        objs = common.get_coll(
            full_query=User.query,
            schema=UserSchema(many=True),
            **args,
        )
        return objs

    #@jwt_required
    def post(self):
        args = parser.parse(_USER_PASS_ARGS, request,
            locations=('form', 'json'))
        if User.query.filter_by(username=args['username']).first():
            return mk_errors(
                400, 'username \'{}\' already taken'.format(args['username']))
        if User.query.filter_by(email=args['email']).first():
            return mk_errors(
                400, 'email \'{}\' already taken'.format(args['email']))
        user = User.create_and_save(**args)
        obj = {
            'data': UserSchema().dump(user),
        }
        return obj


class UserRes(Resource):
    #@jwt_required
    def get(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            return mk_errors(404, 'user id={} does not exist'.format(user_id))
        data = UserSchema().dump(user)
        obj = {
            'data': data,
        }
        return obj

    #@jwt_required
    def delete(self, user_id):
        #check_priviledges()
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            return mk_errors(404, 'user id={} does not exist'.format(user_id))
        db.session.delete(user)
        db.session.commit()
        return '', 204
