from webargs.flaskparser import parser
from webargs.fields import (
    Str,
    Int,
    DelimitedList,
)
from marshmallow import (
    ValidationError,
)
from sqlalchemy import exc
from webargs import validate
from nv.util import (
    filter_fields,
    mk_errors,
    fmt_validation_error_messages,
)
from nv.database import db

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
        key = '{}'.format(date_field)
    elif by == 'oldest':
        key = '{} desc'.format(date_field)
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


def generic_get(model_cls, uid, schema):
    obj = model_cls.query.get(uid)
    if obj is None:
        return mk_errors(404, 'elem id={} does not exist'.format(uid))
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


def generic_put(model_cls, uid, schema, data):
    obj = model_cls.query.get(uid)
    if obj is None:
        return mk_errors(404, 'elem id={} does not exist'.format(uid))
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


def generic_delete(model_cls, uid):
    obj = model_cls.query.get(uid)
    if obj is None:
        return mk_errors(404, 'elem id={} does not exist'.format(uid))
    db.session.delete(obj)
    db.session.commit()
    return '', 204
