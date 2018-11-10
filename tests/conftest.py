import pytest
from nv.app import get_app
from flask_jwt_extended import create_access_token, create_refresh_token

@pytest.fixture()
def app():
    #setup
    app = get_app(config.get_app_test_config_class())
    with app.app_context():
        db.create_all()
        User.create_and_save('su', 'testpass')
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
def client_with_tok(app):
    with app.test_client() as c:
        with app.app_context():
            token = create_access_token(identity='testuser')
            c.get = decorate_crud(c.get, token)
            c.post = decorate_crud(c.post, token)
            c.delete = decorate_crud(c.delete, token)
            c.put = decorate_crud(c.put, token)
        yield c

@pytest.fixture()
def client_with_refresh_tok(app):
    with app.test_client() as c:
        with app.app_context():
            token = create_refresh_token(identity='testuser')
            c.get = decorate_crud(c.get, token)
            c.post = decorate_crud(c.post, token)
            c.delete = decorate_crud(c.delete, token)
            c.put = decorate_crud(c.put, token)
        yield c

@pytest.fixture()
def su_with_tok(app):
    with app.test_client() as c:
        with app.app_context():
            token = create_access_token(identity='su')
            c.get = decorate_crud(c.get, token)
            c.post = decorate_crud(c.post, token)
            c.delete = decorate_crud(c.delete, token)
            c.put = decorate_crud(c.put, token)
        yield c
