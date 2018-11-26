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
from nv.schemas import (
    SubforumSchema,
    TopicSchema,
)
from nv.util import (
    mk_errors,
)
from nv.permissions import (
    CreateSubforum,
    EditSubforum,
    DeleteSubforum,
    CreateTopicInSubforum,
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


class SubforumsRes(Resource):
    def get(self):
        args = parse_get_coll_args(request)
        objs = generic_get_coll(
            full_query=Subforum.query,
            schema=SubforumSchema(many=True),
            **args,
        )
        return objs

    @jwt_required
    def post(self):
        user = get_user(username=get_jwt_identity())
        check_permissions(user, [
            CreateSubforum(),
        ])
        data = request.form.to_dict()
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
        check_permissions(user, [
            DeleteSubforum(subforum),
        ])
        ret = generic_delete(
            obj=subforum,
        )
        return ret

    @jwt_required
    def put(self, subforum_id):
        user = get_user(username=get_jwt_identity())
        subforum = get_obj(Subforum.query.filter_by(subforum_id=subforum_id))
        check_permissions(user, [
            EditSubforum(subforum, attributes=set(request.form)),
        ])
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
        args = parse_get_topics_args(request)
        ret = get_topics(
            full_query=Topic.query.filter_by(subforum_id=subforum_id),
            **args
        )
        return ret

    @jwt_required
    def post(self, subforum_id):
        subforum = get_obj(Subforum.query.filter_by(subforum_id=subforum_id),
            'subforum does not exist')
        user = get_user(username=get_jwt_identity())
        check_permissions(user, [
            CreateTopicInSubforum(subforum),
        ])
        check_post_time_interval(user, Topic)
        #validating/updating data
        data = request.form.to_dict()
        data['user_id'] = user.user_id
        data['subforum_id'] = subforum.subforum_id
        schema = TopicSchema()
        errors = schema.validate(data)
        if errors:
            return mk_errors(400, fmt_validation_error_messages(errors))
        ret = generic_post(
            schema=schema,
            data=data,
        )
        #updating number of topics by user
        user.n_topics += 1
        user.save()
        return ret
