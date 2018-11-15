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
from nv.schemas import (
    AvatarSchema,
)
from nv.util import (
    mk_errors,
)
from nv.permissions import (
    CreateAvatar,
    EditAvatar,
    DeleteAvatar,
)
from nv.database import db
from nv.resources.common import (
    parse_get_coll_args,
    generic_get_coll,
    generic_get,
    generic_post,
    generic_put,
    generic_delete,
    get_user,
    get_obj,
    check_permissions,
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
        check_permissions(user, [
            CreateAvatar(),
        ])
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
        avatar = get_obj(Avatar.query.filter_by(avatar_id=avatar_id),
            'avatar does not exist')
        check_permissions(user, [
            DeleteAvatar(avatar),
        ])
        ret = generic_delete(
            obj=Avatar.query.get(avatar_id),
        )
        return ret

    @jwt_required
    def put(self, avatar_id):
        user = get_user(username=get_jwt_identity())
        avatar = get_obj(Avatar.query.filter_by(avatar_id=avatar_id),
            'avatar does not exist')
        check_permissions(user, [
            EditAvatar(avatar, attributes=set(request.form)),
        ])
        ret = generic_put(
            obj=Avatar.query.get(avatar_id),
            schema=AvatarSchema(),
            data=request.form
        )
        return ret
