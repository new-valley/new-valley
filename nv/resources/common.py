from webargs.flaskparser import parser
from webargs.fields import (
    Str,
    Int,
    DelimitedList,
)
from webargs import validate
from nv.util import (
    filter_fields,
)

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

def get_coll(
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

