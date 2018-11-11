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
    Avatar,
)
from nv.serializers import (
    AvatarSchema,
)
from nv.util import (
    mk_errors,
)
from nv.database import db
from nv import config
from nv.resources import common


class AvatarsRes(Resource):
    def get(self):
        args = common.parse_get_coll_args(request)
        objs = common.get_coll(
            full_query=Avatar.query,
            schema=AvatarSchema(many=True),
            **args,
        )
        return objs