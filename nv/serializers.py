from marshmallow_sqlalchemy import (
    ModelSchema,
    field_for,
)
from marshmallow import (
    EXCLUDE,
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


class UserSchema(ModelSchema):
    user_id = field_for(User, 'user_id', dump_only=True)
    username = field_for(User, 'username', required=True)
    email = field_for(User, 'email', required=True, validator=Email,
        load_only=True)
    roles = Method('split_roles_by_commas')
    status = field_for(User, 'status')
    avatar = Nested(
        AvatarSchema, many=False, dump_only=True, exclude=['users'])
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
        exclude = ['password', 'updated_at']

    
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
