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
api.add_resource(avatars.AvatarRes, '/avatars/<int:avatar_id>')
#users
api.add_resource(users.UsersRes, '/users')
api.add_resource(users.UserRes, '/users/<int:user_id>')
api.add_resource(users.UserPostsRes, '/users/<int:user_id>/posts')
#subforums
api.add_resource(subforums.SubforumsRes, '/subforums')
api.add_resource(subforums.SubforumRes, '/subforums/<int:subforum_id>')
#topics
api.add_resource(topics.TopicsRes, '/topics')
#posts
api.add_resource(posts.PostsRes, '/posts')
api.add_resource(posts.PostRes, '/posts/<int:post_id>')
#auth
api.add_resource(auth.Login, '/auth/login')
api.add_resource(auth.TokenRefresh, '/auth/token_refresh')
api.add_resource(auth.LogoutAccess, '/auth/logout')
#api.add_resource(auth.LogoutRefresh, '/auth/logout/refresh')
api.add_resource(auth.Ok, '/auth/ok')
