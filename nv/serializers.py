from marshmallow_sqlalchemy import (
    ModelSchema,
    field_for,
)
from marshmallow import (
    EXCLUDE,
    pre_load,
    post_load,
    post_dump,
    pre_dump,
    validates,
    ValidationError,
)
from marshmallow.fields import (
    Nested,
    List,
    String,
    Method,
)
from marshmallow.validate import (
    Email,
)
from nv.database import db
from nv.models import (
    Avatar,
    User,
    Subforum,
    Topic,
    Post,
)


class AvatarSchema(ModelSchema):
    avatar_id = field_for(Avatar, 'avatar_id', dump_only=True)
    uri = field_for(Avatar, 'uri', required=True)
    category = field_for(Avatar, 'category', required=True)
    created_at = field_for(Avatar, 'created_at', dump_only=True)
    updated_at = field_for(Avatar, 'updated_at', dump_only=True)

    class Meta:
        unknown = EXCLUDE
        model = Avatar
        sqla_session = db.session
        exclude = ['users']


class UserSchema(ModelSchema):
    user_id = field_for(User, 'user_id', dump_only=True)
    username = field_for(User, 'username', required=True)
    password = field_for(User, 'password', required=True, load_only=True)
    email = field_for(User, 'email', required=True, validator=Email,
        load_only=True)
    roles = Method('split_roles_by_commas')
    status = field_for(User, 'status')
    avatar_id = field_for(User, 'avatar_id', required=True, load_only=True)
    avatar = Nested(
        AvatarSchema, many=False, exclude=['users'], dump_only=True)
    signature = field_for(User, 'signature', required=True)
    created_at = field_for(User, 'created_at', dump_only=True)
    updated_at = field_for(User, 'updated_at', dump_only=True)

    def split_roles_by_commas(self, obj):
        roles = [r.strip() for r in obj.roles.split(',') if r.strip()]
        return roles

    class Meta:
        unknown = EXCLUDE
        model = User
        sqla_session = db.session
        exclude = ['posts']

    
class SubforumSchema(ModelSchema):
    subforum_id = field_for(Subforum, 'subforum_id', dump_only=True)
    title = field_for(Subforum, 'title', required=True)
    description = field_for(Subforum, 'description', required=True)
    position = field_for(Subforum, 'position', required=True)
    created_at = field_for(Subforum, 'created_at', dump_only=True)
    updated_at = field_for(Subforum, 'updated_at', dump_only=True)

    class Meta:
        unknown = EXCLUDE
        model = Subforum
        sqla_session = db.session
        exclude = ['topics']


class TopicSchema(ModelSchema):
    topic_id = field_for(Topic, 'topic_id', dump_only=True)
    title = field_for(Topic, 'title', required=True)
    status = field_for(Topic, 'status', required=True)
    subforum_id = field_for(Topic, 'subforum_id', required=True, load_only=True)
    subforum = Nested(
        SubforumSchema, many=False, exclude=['topics'], dump_only=True)
    created_at = field_for(Topic, 'created_at', dump_only=True)
    updated_at = field_for(Topic, 'updated_at', dump_only=True)

    class Meta:
        unknown = EXCLUDE
        model = Topic
        sqla_session = db.session
        exclude = ['posts']


class PostSchema(ModelSchema):
    post_id = field_for(Post, 'post_id', dump_only=True)
    content = field_for(Post, 'content', required=True)
    status = field_for(Post, 'status', required=True)
    user_id = field_for(Post, 'user_id', required=True, load_only=True)
    user = Nested(
        UserSchema, many=False, dump_only=True, exclude=['posts'])
    topic_id = field_for(Post, 'topic_id', required=True, load_only=True)
    topic = Nested(
        TopicSchema, many=False, dump_only=True, exclude=['posts'])
    created_at = field_for(Topic, 'created_at', dump_only=True)
    updated_at = field_for(Topic, 'updated_at', dump_only=True)

    class Meta:
        unknown = EXCLUDE
        model = Post
        sqla_session = db.session
