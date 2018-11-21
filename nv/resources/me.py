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
)
from nv.schemas import (
    UserSchema,
)
from nv.resources.common import (
    generic_get,
    get_user,
)


class MeRes(Resource):
    @jwt_required
    def get(self):
        user = get_user(username=get_jwt_identity())
        ret = generic_get(
            obj=user,
            schema=UserSchema(),
        )
        return ret
