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
)
from nv.serializers import (
    TopicSchema,
)
from nv.util import (
    mk_errors,
)
from nv.database import db
from nv import config


class TopicsRes(Resource):
    def get(self):
        topics = Topic.query.all()
        data = TopicSchema(many=True).dump(topics)
        obj = {
            'data': data,
            'offset': None,
            'total': len(data),
        }
        return obj
