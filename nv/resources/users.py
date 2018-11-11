from flask import request
from flask_restful import (
    Resource,
)
from sqlalchemy import exc
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt
)
from marshmallow import (
    ValidationError,
)
from nv.models import (
    User,
)
from nv.serializers import (
    UserSchema,
)
from nv.util import (
    mk_errors,
    fmt_validation_error_messages,
)
from nv.resources import common
from nv.database import db
from nv import config

#def check_priviledges():
#    if not get_jwt_identity() in config.superusers:
#        abort(401, 'unauthorized user')


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
        schema = UserSchema()
        try:
            user = schema.load(request.form)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        try:
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            return mk_errors(400, '{}'.format(e.args))
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

    #@jwt_required
    def put(self, user_id):
        #check_priviledges()
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            return mk_errors(404, 'user id={} does not exist'.format(user_id))
        schema = UserSchema()
        try:
            text = schema.load(request.form, instance=user, partial=True)
            db.session.add(user)
            db.session.commit()
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        except exc.IntegrityError as e:
            db.session.rollback()
            return mk_errors(400, '{}'.format(e.args))
        return schema.dump(user)
