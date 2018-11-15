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
    Topic,
    Subforum,
    Post,
)
from nv.serializers import (
    TopicSchema,
    PostSchema,
)
from nv.util import (
    mk_errors,
    fmt_validation_error_messages,
)
from nv.permissions import (
    EditTopic,
    DeleteTopic,
    CreatePostInTopic,
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


class TopicsRes(Resource):
    def get(self):
        args = parse_get_coll_args(request)
        objs = generic_get_coll(
            full_query=Topic.query,
            schema=TopicSchema(many=True),
            **args,
        )
        return objs


class TopicRes(Resource):
    def get(self, topic_id):
        ret = generic_get(
            obj=Topic.query.get(topic_id),
            schema=TopicSchema(),
        )
        return ret

    @jwt_required
    def delete(self, topic_id):
        user = get_user(username=get_jwt_identity())
        topic = get_obj(Topic.query.filter_by(topic_id=topic_id))
        check_permissions(user, [
            DeleteTopic(topic),
        ])
        ret = generic_delete(
            obj=topic,
        )
        return ret

    @jwt_required
    def put(self, topic_id):
        user = get_user(username=get_jwt_identity())
        topic = get_obj(
            Topic.query.filter_by(topic_id=topic_id), 'topic not found')
        check_permissions(user, [
            EditTopic(topic, attributes=set(request.form)),
        ])
        ret = generic_put(
            obj=topic,
            schema=TopicSchema(),
            data=request.form
        )
        return ret


class TopicPostsRes(Resource):
    def get(self, topic_id):
        topic = get_obj(
            Topic.query.filter_by(topic_id=topic_id), 'topic does not exist')
        args = parse_get_coll_args(request)
        ret = generic_get_coll(
            full_query=Post.query.filter_by(topic_id=topic_id),
            schema=PostSchema(many=True),
            **args
        )
        return ret

    @jwt_required
    def post(self, topic_id):
        topic = get_obj(
            Topic.query.filter_by(topic_id=topic_id), 'topic does not exist')
        user = get_user(username=get_jwt_identity())
        check_permissions(user, [
            CreatePostInTopic(topic),
        ])
        #validating/updating data
        data = {k: v[0] for k, v in dict(request.form).items()}
        data['user_id'] = user.user_id
        data['topic_id'] = topic.topic_id
        schema = PostSchema()
        errors = schema.validate(data)
        if errors:
            return mk_errors(400, fmt_validation_error_messages(errors))
        ret = generic_post(
            schema=schema,
            data=data,
        )
        return ret
