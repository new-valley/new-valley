from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager

db = SQLAlchemy()

jwt = JWTManager()

from nv.resources import (
    auth,
    users,
    subforums,
    topics,
    posts,
    avatars,
)
api = Api(prefix='/api')
#avatars
api.add_resource(avatars.AvatarsRes, '/avatars')
#users
api.add_resource(users.UsersRes, '/users')
api.add_resource(users.UserRes, '/users/<int:user_id>')
#subforums
api.add_resource(subforums.SubforumsRes, '/subforums')
#topics
api.add_resource(topics.TopicsRes, '/topics')
#posts
api.add_resource(posts.PostsRes, '/posts')
#auth
api.add_resource(auth.Login, '/auth/login')
api.add_resource(auth.TokenRefresh, '/auth/token_refresh')
api.add_resource(auth.LogoutAccess, '/auth/logout')
#api.add_resource(auth.LogoutRefresh, '/auth/logout/refresh')
api.add_resource(auth.Ok, '/auth/ok')
