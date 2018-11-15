import os
import datetime as dt

app_name = 'newvalley'


env = os.environ.get('NEWVALLEY_ENV', 'development')
assert env in {'development', 'production'}


def _is_dev():
    return env == 'development'


def _is_prod():
    return env == 'production'


def _get_var(key, default=None, conf=os.environ):
    if not _is_dev() and not key in conf:
        raise ValueError('var {} should be in env for production'.format(key))
    return conf.get(key, default)


debug = _is_dev()


class BaseAppConfig:
    PROPAGATE_EXCEPTIONS = True
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DELTA = dt.timedelta(
        hours=int(os.environ.get('NEWVALLEY_JWT_EXPIRATION_DELTA_HOURS', 24)))


def get_app_config_class(**override_environ):
    conf = os.environ.copy()
    conf.update(**override_environ)
    class AppConfig(BaseAppConfig):
        environ = env
        DEBUG = _is_dev()
        TESTING = False
        SECRET_KEY = _get_var(
            'NEWVALLEY_SECRET_KEY', 'secret', conf)
        JWT_SECRET_KEY = _get_var(
            'NEWVALLEY_JWT_SECRET_KEY', 'jwtsecret', conf)
        SQLALCHEMY_DATABASE_URI = _get_var(
            'NEWVALLEY_DB_PATH', 'sqlite:////tmp/newvalleydev.db', conf)
        SQLALCHEMY_TRACK_MODIFICATIONS = _is_prod()
    return AppConfig


def get_app_test_config_class(**override_environ):
    class AppTestConfig(BaseAppConfig):
        environ = 'test'
        DEBUG = True
        TESTING = True
        SECRET_KEY = 'secret'
        JWT_SECRET_KEY = 'jwtsecret'
        SQLALCHEMY_DATABASE_URI = 'sqlite://'
    return AppTestConfig
