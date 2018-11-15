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
    Topic,
)
from nv.serializers import (
    PostSchema,
)
from nv.util import (
    mk_errors,
)
from nv.permissions import (
    EditPost,
    DeletePost,
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
        topic = get_obj(Topic.query.filter_by(topic_id=post.topic_id))
        check_permissions(user, [
            DeletePost(post),
        ])
        ret = generic_delete(
            obj=post,
        )
        return ret

    @jwt_required
    def put(self, post_id):
        user = get_user(username=get_jwt_identity())
        post = get_obj(Post.query.filter_by(post_id=post_id))
        topic = get_obj(Topic.query.filter_by(topic_id=post.topic_id))
        check_permissions(user, [
            EditPost(post, attributes=set(request.form)),
        ])
        ret = generic_put(
            obj=post,
            schema=PostSchema(exclude=('user_id', 'topic_id')),
            data=request.form
        )
        return ret
