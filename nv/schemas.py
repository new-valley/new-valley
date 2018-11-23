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
from marshmallow.validate import (
    Range,
)
from marshmallow.fields import (
    Nested,
    List,
    String,
    Email,
    DateTime,
    Integer,
)
from nv.database import db
from nv.models import (
    Avatar,
    User,
    Subforum,
    Topic,
    Post,
)
from nv.util import generate_hash, get_datetime


class LocalizedDateTime(DateTime):
    def __init__(self, **kwargs):
        super().__init__(format='iso', **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return super()._serialize(value, attr, obj, **kwargs)
        return get_datetime(value).isoformat()

    def _deserialize(self, value, attr, obj, **kwargs):
        if not value:
            return super()._deserialize(value, attr, obj, **kwargs)
        return get_datetime(value)


class AvatarSchema(ModelSchema):
    avatar_id = String(dump_only=True)
    uri = field_for(Avatar, 'uri', required=True)
    category = field_for(Avatar, 'category', required=True)
    created_at = LocalizedDateTime(dump_only=True)
    updated_at = LocalizedDateTime(dump_only=True)

    class Meta:
        unknown = EXCLUDE
        model = Avatar
        sqla_session = db.session
        exclude = ['users']


def _split_by_commas(string):
    tokens = [t.strip() for t in string.split(',') if t.strip()]
    return tokens


class UserSchema(ModelSchema):
    user_id = String(dump_only=True)
    username = field_for(User, 'username', required=True)
    password = field_for(User, 'password', required=True, load_only=True)
    email = Email(required=True, load_only=True)
    roles = field_for(User, 'roles')
    status = field_for(User, 'status')
    avatar_id = field_for(User, 'avatar_id', required=True, load_only=True)
    avatar = Nested(
        AvatarSchema, many=False, exclude=['users'], dump_only=True)
    signature = field_for(User, 'signature', required=False)
    n_posts = field_for(User, 'n_posts')
    n_topics = field_for(User, 'n_topics')
    created_at = LocalizedDateTime(dump_only=True)
    updated_at = LocalizedDateTime(dump_only=True)

    @validates('password')
    def check_password_len(self, password):
        if len(password) < User.MIN_UNHASHED_PASSWORD_LEN:
            raise ValidationError(
                'password should be at least {} chars long'.format(
                    User.MIN_UNHASHED_PASSWORD_LEN))

    @validates('roles')
    def check_roles(self, roles):
        roles = _split_by_commas(roles)
        if not roles:
            raise ValidationError('set of roles cannot be empty')
        for role in roles:
            if not role in User.VALID_ROLES:
                raise ValidationError('role \'{}\' is invalid'.format(role))

    @validates('status')
    def check_status(self, status):
        if not status in User.VALID_STATUSES:
            raise ValidationError('status \'{}\' is invalid'.format(status))

    @validates('avatar_id')
    def check_avatar_exists(self, avatar_id):
        if not Avatar.query.filter_by(avatar_id=avatar_id).first():
            raise ValidationError(
                'avatar id={} does not exist'.format(avatar_id))

    @post_load
    def clean_roles(self, data):
        if 'roles' in data:
            roles = set(_split_by_commas(data['roles']))
            data['roles'] = ','.join(roles)
        return data

    @post_dump
    def split_roles_by_commas(self, data):
        data['roles'] = _split_by_commas(data['roles'])
        return data

    @post_load
    def hash_password(self, data):
        if 'password' in data:
            data['password'] = generate_hash(data['password'])
        return data

    class Meta:
        unknown = EXCLUDE
        model = User
        sqla_session = db.session
        exclude = ['posts', 'topics']


class SubforumSchema(ModelSchema):
    subforum_id = String(dump_only=True)
    title = field_for(Subforum, 'title', required=True)
    description = field_for(Subforum, 'description', required=True)
    position = field_for(
        Subforum, 'position', required=not True, validate=Range(min=1))
    n_topics = Integer(dump_only=True)
    created_at = LocalizedDateTime(dump_only=True)
    updated_at = LocalizedDateTime(dump_only=True)

    @post_dump
    def set_n_topics(self, data):
        if 'subforum_id' in data:
            n_topics = \
                Topic.query.filter_by(subforum_id=data['subforum_id']).count()
            data['n_topics'] = n_topics
        return data

    class Meta:
        unknown = EXCLUDE
        model = Subforum
        sqla_session = db.session
        exclude = ['topics']


class TopicSchema(ModelSchema):
    topic_id = String(dump_only=True)
    title = field_for(Topic, 'title', required=True)
    status = field_for(Topic, 'status')
    user_id = field_for(Topic, 'user_id', required=True, load_only=True)
    user = Nested(
        UserSchema, many=False, dump_only=True)
    subforum_id = field_for(
        Topic, 'subforum_id', required=True, load_only=True)
    subforum = Nested(
        SubforumSchema, many=False, dump_only=True)
    n_posts = Integer(dump_only=True)
    created_at = LocalizedDateTime(dump_only=True)
    updated_at = LocalizedDateTime(dump_only=True)

    @validates('status')
    def check_status(self, status):
        if not status in Topic.VALID_STATUSES:
            raise ValidationError('status \'{}\' is invalid'.format(status))

    @post_dump
    def set_n_posts(self, data):
        if 'topic_id' in data:
            n_posts = Post.query.filter_by(topic_id=data['topic_id']).count()
            data['n_posts'] = n_posts
        return data

    class Meta:
        unknown = EXCLUDE
        model = Topic
        sqla_session = db.session
        exclude = ['posts']


class PostSchema(ModelSchema):
    post_id = String(dump_only=True)
    content = field_for(Post, 'content', required=True)
    status = field_for(Post, 'status')
    user_id = field_for(Post, 'user_id', required=True, load_only=True)
    user = Nested(UserSchema, many=False, dump_only=True)
    topic_id = field_for(Post, 'topic_id', required=True, load_only=True)
    topic = Nested(TopicSchema, many=False, dump_only=True)
    created_at = LocalizedDateTime(dump_only=True)
    updated_at = LocalizedDateTime(dump_only=True)

    @validates('status')
    def check_status(self, status):
        if not status in Post.VALID_STATUSES:
            raise ValidationError('status \'{}\' is invalid'.format(status))

    class Meta:
        unknown = EXCLUDE
        model = Post
        sqla_session = db.session
