from flask import request
from flask_restful import (
    Resource,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from webargs.flaskparser import parser
from webargs.fields import (
    Str,
    Int,
)
from webargs import validate
from nv.models import (
    Avatar,
)
from nv.serializers import (
    AvatarSchema,
)
from nv.util import (
    mk_errors,
)
from nv.database import db
from nv import config
from nv.resources.common import (
    parse_get_coll_args,
    generic_get_coll,
    generic_get,
    generic_post,
    generic_put,
    generic_delete,
    get_user,
    is_admin,
    is_moderator,
)

class AvatarsRes(Resource):
    def get(self):
        args = parse_get_coll_args(request)
        objs = generic_get_coll(
            full_query=Avatar.query,
            schema=AvatarSchema(many=True),
            **args,
        )
        return objs

    @jwt_required
    def post(self):
        user = get_user(username=get_jwt_identity())
        if not is_admin(user):
            return mk_errors(401, 'operation not allowed for user')
        ret = generic_post(
            schema=AvatarSchema(),
            data=request.form,
        )
        return ret

class AvatarRes(Resource):
    def get(self, avatar_id):
        ret = generic_get(
            obj=Avatar.query.get(avatar_id),
            schema=AvatarSchema(),
        )
        return ret

    @jwt_required
    def delete(self, avatar_id):
        user = get_user(username=get_jwt_identity())
        if not is_admin(user):
            return mk_errors(401, 'operation not allowed for user')
        ret = generic_delete(
            obj=Avatar.query.get(avatar_id),
        )
        return ret

    @jwt_required
    def put(self, avatar_id):
        user = get_user(username=get_jwt_identity())
        if not is_admin(user):
            return mk_errors(401, 'operation not allowed for user')
        ret = generic_put(
            obj=Avatar.query.get(avatar_id),
            schema=AvatarSchema(),
            data=request.form
        )
        return ret
