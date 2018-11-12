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


#def _user_can_create_topic(user, subforum=None):
#    return is_admin(user) or is_moderator(user) or user.status == 'active'


def _user_can_delete_topic(user, topic):
    return is_admin(user) or is_moderator(user) or \
        user.user_id == topic.user_id


def _user_can_edit_topic(user, topic):
    is_author_and_can_edit = user.user_id == topic.user_id \
        and user.status == 'active' \
        and topic.status == 'published'
    return is_admin(user) or is_moderator(user) or is_author_and_can_edit


def _user_can_create_post(user, topic):
    return is_admin(user) or is_moderator(user) \
        or (user.status == 'active' and topic.status == 'published')


class TopicsRes(Resource):
    def get(self):
        args = parse_get_coll_args(request)
        objs = generic_get_coll(
            full_query=Topic.query,
            schema=TopicSchema(many=True),
            **args,
        )
        return objs

    '''@jwt_required
    def post(self):
        user = get_user(username=get_jwt_identity())
        #validating/updating data
        data = {k: v[0] for k, v in dict(request.form).items()}
        data['user_id'] = user.user_id
        schema = TopicSchema()
        errors = schema.validate(data)
        if errors:
            return mk_errors(400, fmt_validation_error_messages(errors))
        #check if subforum exists
        subforum = get_obj(
            Subforum.query.filter_by(subforum_id=data['subforum_id']))
        #checking if user can create topic
        if not _user_can_create_topic(user, subforum):
            return mk_errors(400, 'user cannot create topic')
        ret = generic_post(
            schema=schema,
            data=data,
        )
        return ret'''


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
        #only the author of the topic or mods/admins can delete
        if not _user_can_delete_topic(user, topic):
            return mk_errors(401, 'operation not allowed for user in topic')
        ret = generic_delete(
            obj=topic,
        )
        return ret

    @jwt_required
    def put(self, topic_id):
        user = get_user(username=get_jwt_identity())
        topic = get_obj(
            Topic.query.filter_by(topic_id=topic_id), 'topic not found')
        #only the topic itself/admins can perform the operation
        if not _user_can_edit_topic(user, topic):
            return mk_errors(401, 'operation not allowed for user in topic')
        #only moderator/admin can alter these properties
        if {'status', 'created_at'} <= set(request.form.keys()) \
            and not (is_admin(user) or is_moderator(user)):
            return mk_errors(401, 'operation not allowed for user in topic')
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
        topic = Topic.query.get(topic_id)
        if topic is None:
            return mk_errors(404, 'topic does not exist')
        user = get_user(username=get_jwt_identity())
        #validating/updating data
        data = {k: v[0] for k, v in dict(request.form).items()}
        data['user_id'] = user.user_id
        data['topic_id'] = topic.topic_id
        schema = PostSchema()
        errors = schema.validate(data)
        if errors:
            return mk_errors(400, fmt_validation_error_messages(errors))
        #checking if user can create post
        if not _user_can_create_post(user, topic):
            return mk_errors(400, 'user cannot create post')
        ret = generic_post(
            schema=schema,
            data=data,
        )
        return ret
