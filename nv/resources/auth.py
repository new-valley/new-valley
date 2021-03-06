from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt
)
from flask import (
    request,
    abort,
)
from nv.util import (
    mk_errors,
    mk_message,
    verify_hash,
)
from nv.models import User, RevokedToken
from nv.schemas import UserSchema
from nv.database import db
from nv.extensions import jwt


class Login(Resource):
    def post(self):
        '''
        Login into system.
        '''
        args = request.form
        if not 'password' in args:
            return mk_errors(400, 'email is required')
        if 'username' in args:
            user = User.query.filter_by(username=args['username']).first()
        elif 'email' in args:
            user = User.query.filter_by(email=args['email']).first()
        else:
            return mk_errors(400, 'email or username are required')
        if user is None or not verify_hash(args['password'], user.password):
            return mk_errors(400, 'invalid credentials')
        access_tok = create_access_token(identity=user.username)
        refresh_tok = create_refresh_token(identity=user.username)
        return {
            'access_token': access_tok,
            'refresh_token': refresh_tok,
        }


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        '''
        Refresh access token.
        '''
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}, 200


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklisted(jti)


class LogoutAccess(Resource):
    @jwt_required
    def post(self):
        '''
        Revoke access token.
        '''
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.save()
            return '', 204
        except Exception as e:
            print('WTF: {}'.format(e))
            return mk_errors(500, 'error in logout')


class Ok(Resource):
    @jwt_required
    def get(self):
        return mk_message('ok')
