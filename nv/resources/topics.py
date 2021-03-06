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
from nv.schemas import (
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
    parse_get_topics_args,
    get_topics,
    generic_get,
    generic_post,
    generic_put,
    generic_delete,
    get_user,
    get_obj,
    check_permissions,
    check_post_time_interval,
)


class TopicsRes(Resource):
    def get(self):
        args = parse_get_topics_args(request)
        ret = get_topics(
            full_query=Topic.query,
            **args,
        )
        return ret


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
        #updating number of topics by user
        user.n_topics = max(user.n_topics - 1, 0)
        user.save()
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
        check_post_time_interval(user, Post)
        #validating/updating data
        data = request.form.to_dict()
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
        #updating number of posts by user
        user.n_posts += 1
        user.save()
        return ret
