from flask import request
from flask_restful import (
    Resource,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from nv.models import (
    User,
    Avatar,
    Post,
    Topic,
)
from nv.serializers import (
    UserSchema,
    PostSchema,
    TopicSchema,
)
from nv.util import (
    mk_errors,
)
from nv.resources.common import (
    parse_get_coll_args,
    generic_get_coll,
    generic_get,
    generic_post,
    generic_put,
    generic_delete,
    get_user,
    check_permissions,
)
from nv.permissions import (
    DeleteUser,
    EditUser,
)
from nv.database import db


class UsersRes(Resource):
    def get(self):
        args = parse_get_coll_args(request)
        ret = generic_get_coll(
            full_query=User.query,
            schema=UserSchema(many=True),
            **args,
        )
        return ret

    def post(self):
        data = {k: v[0] for k, v in dict(request.form).items()}
        #default avatar to be chosen
        if not 'avatar_id' in data:
            data['avatar_id'] = Avatar.query.first().avatar_id
        ret = generic_post(
            schema=UserSchema(),
            data=data,
        )
        return ret


class UserRes(Resource):
    def get(self, user_id):
        ret = generic_get(
            obj=User.query.get(user_id),
            schema=UserSchema(),
        )
        return ret

    @jwt_required
    def delete(self, user_id):
        user = get_user(username=get_jwt_identity())
        target_user = get_user(user_id=user_id)
        check_permissions(user, [
            DeleteUser(target_user),
        ])
        ret = generic_delete(
            obj=target_user,
        )
        return ret

    @jwt_required
    def put(self, user_id):
        user = get_user(username=get_jwt_identity())
        target_user = get_user(user_id=user_id)
        #EditUser(target=target_user, attributes=set(request.form)).check(user)
        check_permissions(user, [
            EditUser(target_user, attributes=set(request.form)),
        ])
        ret = generic_put(
            obj=target_user,
            schema=UserSchema(),
            data=request.form
        )
        return ret


class UserPostsRes(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user is None:
            return mk_errors(404, 'user does not exist')
        args = parse_get_coll_args(request)
        ret = generic_get_coll(
            full_query=Post.query.filter_by(user_id=user_id),
            schema=PostSchema(many=True),
            **args
        )
        return ret


class UserTopicsRes(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user is None:
            return mk_errors(404, 'user does not exist')
        args = parse_get_coll_args(request)
        ret = generic_get_coll(
            full_query=Topic.query.filter_by(user_id=user_id),
            schema=TopicSchema(many=True),
            **args
        )
        return ret
