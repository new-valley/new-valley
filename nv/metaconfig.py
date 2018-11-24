import os
import datetime as dt

app_name = 'newvalley'


_env = os.environ.get('NEWVALLEY_ENV', 'development')
assert _env in {'development', 'production'}


def _is_dev():
    return _env == 'development'


def _is_prod():
    return _env == 'production'


def _get_var(key, default=None, conf=os.environ):
    if not _is_dev() and not key in conf:
        raise ValueError('var {} should be in env for production'.format(key))
    return conf.get(key, default)


class BaseAppConfig:
    ENV = _env
    PROPAGATE_EXCEPTIONS = True
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #jwt expiration time, in seconds
    JWT_ACCESS_TOKEN_EXPIRES = dt.timedelta(
        seconds=int(os.environ.get(
            'NEWVALLEY_JWT_ACCESS_EXPIRATION_TIME', 24*60*60)))
    JWT_REFRESH_TOKEN_EXPIRES = dt.timedelta(
        seconds=int(os.environ.get(
            'NEWVALLEY_JWT_REFRESH_EXPIRATION_TIME', 24*60*60)))
    #minimum posting time interval in seconds for posts and topics creation
    MIN_POST_TIME_INTERVAL = int(
        os.environ.get('NEWVALLEY_MIN_POST_TIME_INTERVAL', 30))


def get_app_config_class(**override_environ):
    conf = os.environ.copy()
    conf.update(**override_environ)
    class AppConfig(BaseAppConfig):
        ENV = _env
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
        ENV = 'test'
        DEBUG = True
        TESTING = True
        SECRET_KEY = 'secret'
        JWT_SECRET_KEY = 'jwtsecret'
        SQLALCHEMY_DATABASE_URI = 'sqlite://'
        MIN_POST_TIME_INTERVAL = 0
    return AppTestConfig
