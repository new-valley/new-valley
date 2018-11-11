import pytest
from flask_jwt_extended import create_access_token, create_refresh_token
from nv.app import get_app
from nv import config
from nv.util import generate_hash
from nv.database import db
from nv.models import (
    User,
    Avatar
)


@pytest.fixture()
def app():
    #setup
    app = get_app(config.get_app_test_config_class())
    with app.app_context():
        db.create_all()
        #dummy avatars
        avatar = Avatar.create_and_save(
            uri='http://example.com/img.jpg',
            category='dummy',
        )
        Avatar.create_and_save(
            uri='http://example.com/img2.jpg',
            category='dummy2',
        )
        Avatar.create_and_save(
            uri='http://example.com/img3.png',
            category='dummy',
        )
        #superuser
        User.create_and_save(
            username='admin',
            password=generate_hash('testpass'),
            email='su@superusers.com',
            avatar_id=avatar.avatar_id,
            roles='admin',
        )
        #moderator
        User.create_and_save(
            username='mod',
            password=generate_hash('testpass'),
            email='mod@mods.com',
            avatar_id=avatar.avatar_id,
            roles='moderator',
        )
        #simple users
        User.create_and_save(
            username='user',
            password=generate_hash('testpass'),
            email='user@users.com',
            avatar_id=avatar.avatar_id,
            roles='user',
        )
        User.create_and_save(
            username='user_b',
            password=generate_hash('testpass'),
            email='user_b@users.com',
            avatar_id=avatar.avatar_id,
            roles='user',
        )
        app.dummy_avatar_id = avatar.avatar_id
    yield app
    #teardown
    with app.app_context():
        db.session.remove()
        db.drop_all()


def decorate_crud(fn, token):
    def wrapper(*args, **kwargs):
        if not 'headers' in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['Authorization'] = 'Bearer {}'.format(token)
        return fn(*args, **kwargs)
    return wrapper


@pytest.fixture()
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture()
def avatar_id(app):
    with app.app_context():
        avatar_id = Avatar.query.first().avatar_id
    yield avatar_id


def _user_id_getter(app):
    def wrapper(username='user'):
        with app.app_context():
            user_id = User.query.filter_by(username=username).first().user_id
        return user_id
    return wrapper


@pytest.fixture()
def user_id_getter(app):
    return _user_id_getter(app)


@pytest.fixture()
def user_id(app):
    yield _user_id_getter(app)()


def _access_token_getter(app):
    def wrapper(username='user'):
        with app.app_context():
            access_token = create_access_token(identity=username)
        return access_token
    return wrapper


@pytest.fixture()
def access_token_getter(app):
    return _access_token_getter(app)


@pytest.fixture()
def access_token(app):
    yield _access_token_getter(app)()


def _refresh_token_getter(app):
    def wrapper(username='user'):
        with app.app_context():
            refresh_token = create_refresh_token(identity=username)
        return refresh_token
    return wrapper


@pytest.fixture()
def refresh_token_getter(app):
    return _refresh_token_getter(app)


@pytest.fixture()
def refresh_token(app):
    yield _refresh_token_getter(app)()


def _client_with_tok_getter(app):
    def wrapper(username='user'):
        with app.test_client() as c:
            with app.app_context():
                token = create_access_token(identity=username)
                c.get = decorate_crud(c.get, token)
                c.post = decorate_crud(c.post, token)
                c.delete = decorate_crud(c.delete, token)
                c.put = decorate_crud(c.put, token)
            return c
    return wrapper


def _client_with_refresh_tok_getter(app):
    def wrapper(username='user'):
        with app.test_client() as c:
            with app.app_context():
                token = create_refresh_token(identity=username)
                c.get = decorate_crud(c.get, token)
                c.post = decorate_crud(c.post, token)
                c.delete = decorate_crud(c.delete, token)
                c.put = decorate_crud(c.put, token)
            return c
    return wrapper


@pytest.fixture()
def client_with_tok_getter(app):
    return _client_with_tok_getter(app)


@pytest.fixture()
def client_with_tok(app):
    yield _client_with_tok_getter(app)()


@pytest.fixture()
def mod_with_tok(app):
    yield _client_with_tok_getter(app)('mod')


@pytest.fixture()
def admin_with_tok(app):
    yield _client_with_tok_getter(app)('admin')


@pytest.fixture()
def client_with_refresh_tok_getter(app):
    return _client_with_refresh_tok_getter(app)


@pytest.fixture()
def client_with_refresh_tok(app):
    yield _client_with_refresh_tok_getter(app)()


@pytest.fixture()
def mod_with_refresh_tok(app):
    yield _client_with_refresh_tok_getter(app)('mod')


@pytest.fixture()
def admin_with_refresh_tok(app):
    yield _client_with_refresh_tok_getter(app)('admin')
