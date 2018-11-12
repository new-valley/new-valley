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
    Subforum,
    Topic,
)
from nv.serializers import (
    SubforumSchema,
    TopicSchema,
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
    get_obj,
    is_admin,
    is_moderator,
)

class SubforumsRes(Resource):
    def get(self):
        args = parse_get_coll_args(request)
        objs = generic_get_coll(
            full_query=Subforum.query,
            schema=SubforumSchema(many=True),
            **args,
        )
        return objs

    def post(self):
        data = {k: v[0] for k, v in dict(request.form).items()}
        if not 'position' in data:
            subforum = Subforum.query.order_by(-Subforum.position).first()
            position = 1 if subforum is None else (subforum.position + 1)
            data['position'] = position
        ret = generic_post(
            schema=SubforumSchema(),
            data=data,
        )
        return ret


class SubforumRes(Resource):
    def get(self, subforum_id):
        ret = generic_get(
            obj=Subforum.query.get(subforum_id),
            schema=SubforumSchema(),
        )
        return ret

    @jwt_required
    def delete(self, subforum_id):
        user = get_user(username=get_jwt_identity())
        subforum = get_obj(Subforum.query.filter_by(subforum_id=subforum_id))
        #only admins/mods can perform the operation
        if not is_admin(user):
            return mk_errors(401, 'operation not allowed for user')
        ret = generic_delete(
            obj=subforum,
        )
        return ret

    @jwt_required
    def put(self, subforum_id):
        user = get_user(username=get_jwt_identity())
        subforum = get_obj(Subforum.query.filter_by(subforum_id=subforum_id))
        #only the user itself/admins/mods can perform the operation
        if not is_admin(user):
            return mk_errors(401, 'operation not allowed for user')
        ret = generic_put(
            obj=subforum,
            schema=SubforumSchema(),
            data=request.form
        )
        return ret


class SubforumTopicsRes(Resource):
    def get(self, subforum_id):
        subforum = Subforum.query.get(subforum_id)
        if subforum is None:
            return mk_errors(404, 'subforum does not exist')
        args = parse_get_coll_args(request)
        ret = generic_get_coll(
            full_query=Topic.query.filter_by(subforum_id=subforum_id),
            schema=TopicSchema(many=True),
            **args
        )
        return ret
