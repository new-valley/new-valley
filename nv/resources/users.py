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
from nv.resources.common import (
    parse_get_coll_args,
    generic_get_coll,
    generic_get,
    generic_post,
    generic_put,
    generic_delete,
)
from nv.database import db
from nv import config

#def check_priviledges():
#    if not get_jwt_identity() in config.superusers:
#        abort(401, 'unauthorized user')


class UsersRes(Resource):
    #@jwt_required
    def get(self):
        #check_priviledges()
        args = parse_get_coll_args(request)
        ret = generic_get_coll(
            full_query=User.query,
            schema=UserSchema(many=True),
            **args,
        )
        return ret

    #@jwt_required
    def post(self):
        #check_priviledges()
        ret = generic_post(
            schema=UserSchema(),
            data=request.form
        )
        return ret


class UserRes(Resource):
    #@jwt_required
    def get(self, user_id):
        #check_priviledges()
        ret = generic_get(
            model_cls=User,
            uid=user_id,
            schema=UserSchema(),
        )
        return ret

    #@jwt_required
    def delete(self, user_id):
        #check_priviledges()
        ret = generic_delete(
            model_cls=User,
            uid=user_id,
        )
        return ret

    #@jwt_required
    def put(self, user_id):
        #check_priviledges()
        ret = generic_put(
            model_cls=User,
            uid=user_id,
            schema=UserSchema(),
            data=request.form
        )
        return ret
