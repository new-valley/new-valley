from werkzeug.exceptions import TooManyRequests
from webargs.flaskparser import parser
from webargs.fields import (
    Str,
    Int,
    DelimitedList,
)
from marshmallow import (
    ValidationError,
)
from sqlalchemy import exc, desc
from webargs import validate
from nv.models import (
    User,
)
from flask import abort
from flask import current_app
from nv.util import (
    filter_fields,
    mk_errors,
    fmt_validation_error_messages,
    get_now,
    get_datetime,
)
from nv.database import db
from nv.permissions import BypassAntiFlood


def crop_query(query, offset=None, max_n_results=None):
    if offset is not None:
        query = query.offset(offset)
    if query.count() <= max_n_results:
        new_offset = None
    else:
        new_offset = (0 if offset is None else offset) + max_n_results
    if max_n_results is not None:
        query = query.limit(max_n_results)
    return query, new_offset


DEF_MAX_N_RESULTS = 2048


ORDER_BY_OPTIONS = [
    'newest',
    'oldest',
    None,
]


DEF_GET_COLL_ARGS = {
    'fields': DelimitedList(Str()),
    'offset': Int(validate=lambda n: n >= 0),
    'max_n_results': Int(validate=lambda n: n >= 0, missing=DEF_MAX_N_RESULTS),
    'order': Str(
        validate=validate.OneOf(ORDER_BY_OPTIONS), missing='newest'),
}


def parse_get_coll_args(req, args=DEF_GET_COLL_ARGS,
        locations=('querystring', 'form')):
    args = parser.parse(args, req, locations=locations)
    return args


def order_query(query, by='newest', date_field='created_at'):
    assert by in ORDER_BY_OPTIONS
    if by == 'newest':
        key = desc('{}'.format(date_field))
    elif by == 'oldest':
        key = '{}'.format(date_field)
    else:
        raise ValueError('"by" must bt in {}'.format(ORDER_BY_OPTIONS))
    query = query.order_by(key)
    return query


def generic_get_coll(
        full_query, schema,
        offset=None, max_n_results=None, fields=None, order='newest'):
    total = full_query.count()
    full_query = order_query(full_query, order)
    query, new_offset = crop_query(full_query, offset, max_n_results)
    objs = query.all()
    data = schema.dump(objs)
    data = filter_fields(data, fields)
    return {
        'total': total,
        'offset': new_offset,
        'data': data,
    }


def generic_get(obj, schema):
    if obj is None:
        return mk_errors(404, 'element does not exist')
    data = schema.dump(obj)
    ret = {
        'data': data,
    }
    return ret


def generic_post(schema, data):
    try:
        obj = schema.load(data)
    except ValidationError as e:
        return mk_errors(400, fmt_validation_error_messages(e.messages))
    try:
        db.session.add(obj)
        db.session.commit()
    except exc.IntegrityError as e:
        db.session.rollback()
        return mk_errors(400, '{}'.format(e.args))
    ret = {
        'data': schema.dump(obj),
    }
    return ret


def generic_put(obj, schema, data):
    if obj is None:
        return mk_errors(404, 'element does not exist')
    try:
        obj = schema.load(data, instance=obj, partial=True)
        db.session.add(obj)
        db.session.commit()
    except ValidationError as e:
        return mk_errors(400, fmt_validation_error_messages(e.messages))
    except exc.IntegrityError as e:
        db.session.rollback()
        return mk_errors(400, '{}'.format(e.args))
    ret = {
        'data': schema.dump(obj),
    }
    return ret


def generic_delete(obj):
    if obj is None:
        return mk_errors(404, 'element does not exist')
    db.session.delete(obj)
    db.session.commit()
    return '', 204


def get_obj(query, abort_if_not_found=True, not_found_msg='item not found'):
    obj = query.first()
    if obj is None and abort_if_not_found:
        abort(404, not_found_msg)
    return obj


def get_user(user_id=None, username=None, abort_if_not_found=True):
    assert user_id is not None or username is not None
    if user_id is not None:
        query = User.query.filter_by(user_id=user_id)
        not_found_msg = 'user id={} doest not exist'.format(user_id)
    else:
        query = User.query.filter_by(username=username)
        not_found_msg = 'user username={} doest not exist'.format(username)
    return get_obj(query, abort_if_not_found, not_found_msg)


def check_permissions(user, permissions):
    if not isinstance(permissions, (list, tuple)):
        permissions = [permissions]
    for permission in permissions:
        permission.check(user)


def check_post_time_interval(user, model_cls):
    if BypassAntiFlood.is_granted(user):
        return
    last_post = order_query(
        model_cls.query.filter_by(user_id=user.user_id), by='newest').first()
    if last_post is None:
        return
    diff_secs = (get_now() - get_datetime(last_post.created_at)).total_seconds()
    if int(diff_secs) < current_app.config['MIN_POST_TIME_INTERVAL']:
        raise TooManyRequests('not outside minimum time interval for posting')
