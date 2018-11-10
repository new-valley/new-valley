from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager

db = SQLAlchemy()

jwt = JWTManager()

from nv.resources import (
    auth,
    test,
    users,
)
api = Api(prefix='/api')
#test
api.add_resource(test.Test, '/test')
#users
api.add_resource(users.UsersRes, '/users')
api.add_resource(users.UserRes, '/users/<int:user_id>')
#auth
#api.add_resource(auth.UserRes, '/users/<int:user_id>')
#api.add_resource(auth.UsersRes, '/users')
api.add_resource(auth.Login, '/auth/login')
api.add_resource(auth.TokenRefresh, '/auth/token/refresh')
api.add_resource(auth.LogoutAccess, '/auth/logout/access')
api.add_resource(auth.LogoutRefresh, '/auth/logout/refresh')
api.add_resource(auth.Ok, '/auth/ok')
