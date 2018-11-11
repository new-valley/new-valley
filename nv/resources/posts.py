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
    Post,
)
from nv.serializers import (
    PostSchema,
)
from nv.util import (
    mk_errors,
)
from nv.database import db
from nv import config
from nv.resources import common
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


class PostsRes(Resource):
    def get(self):
        args = parse_get_coll_args(request)
        ret = generic_get_coll(
            full_query=Post.query,
            schema=PostSchema(many=True),
            **args,
        )
        return ret


class PostRes(Resource):
    def get(self, post_id):
        ret = generic_get(
            obj=Post.query.get(post_id),
            schema=PostSchema(),
        )
        return ret

    @jwt_required
    def delete(self, post_id):
        user = get_user(username=get_jwt_identity())
        post = get_obj(Post.query.filter_by(post_id=post_id))
        #only the user itself/admins/mods can perform the operation
        if not (user.user_id == post.user_id \
            or is_admin(user) or is_moderator(user)):
            return mk_errors(401, 'operation not allowed for user')
        ret = generic_delete(
            obj=post,
        )
        return ret

    @jwt_required
    def put(self, post_id):
        user = get_user(username=get_jwt_identity())
        post = get_obj(Post.query.filter_by(post_id=post_id))
        #only the user itself/admins/mods can perform the operation
        if not (user.user_id == post.user_id \
            or is_admin(user) or is_moderator(user)):
            return mk_errors(401, 'operation not allowed for user')
        if {'status', 'created_at'} <= set(request.form.keys()) \
            and not (is_admin(post) or is_moderator(post)):
            return mk_errors(401, 'operation not allowed for user')
        ret = generic_put(
            obj=post,
            schema=PostSchema(exclude=('user_id', 'topic_id')),
            data=request.form
        )
        return ret
