#!/usr/bin/env python3


from nv import app
from nv.models import Avatar, User, Subforum, Post, Topic
from nv.schemas import (
    AvatarSchema,
    UserSchema,
    SubforumSchema,
    PostSchema,
    TopicSchema
)
from nv.models import (
    Avatar,
    User,
    Subforum,
    Post,
    Topic
)
from nv.database import db
from nv.util import get_datetime, flatten
from flask import current_app
import os
import json
import random
import math
import multiprocessing as mp
from functools import partial
import argparse


DEF_SRC_PATH = os.path.join('data', 'fake-data.json')
DEF_MAX_CHUNK_SIZE = 100000
DEF_N_THREADS = mp.cpu_count()


def partition(lst, chunk_size):
    if chunk_size < 1:
        return lst
    lsts = [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]
    #lsts = [l for l in lsts if l]
    return lsts


def get_app(**conf):
    return app.get_app(**conf)


def populate(schema, data):
    objs = schema.load(data)
    if not objs:
        return


def _add_all(objs, data):
    #if present, updating objects with some fields that are not loaded
    #by default by schemas
    id_field = '{}_id'.format(objs[0].__class__.__name__.lower())
    for obj, dct in zip(objs, data):
        if 'created_at' in dct:
            obj.created_at = get_datetime(dct['created_at'])
        if 'updated_at' in dct:
            obj.updated_at = get_datetime(dct['updated_at'])
        if id_field in dct:
            setattr(obj, id_field, dct[id_field])
    db.session.flush()
    db.session.add_all(objs)
    db.session.commit()


def add_all(objs):
    db.session.flush()
    db.session.add_all(objs)
    db.session.commit()


def deserialize(data, model_cls=None):
    new_dct = {}
    for k, v in data.items():
        if k.endswith('_id') or k.startswith('n_'):
            new_dct[k] = int(v)
        elif k.endswith('_at'):
            new_dct[k] = get_datetime(v)
        else:
            new_dct[k] = str(v)
    obj = new_dct if model_cls is None else model_cls(**new_dct)
    return obj


def deserialize_all(data, model_cls, n_threads):
    #return [deserialize(d, model_cls) for d in data]
    fn = partial(deserialize, model_cls=model_cls)
    pool = mp.Pool(n_threads)
    objs = pool.map(fn, data)
    pool.close()
    pool.join()
    return objs


def deserialize_and_add_all(data, model_cls, n_threads):
    objs = deserialize_all(data, model_cls, n_threads)
    add_all(objs)


MODELS = {
    'avatars': Avatar,
    'users': User,
    'subforums': Subforum,
    'topics': Topic,
    'posts': Post,
}


def populate(data, n, total, n_threads):
    for key in ['avatars', 'users', 'subforums', 'topics', 'posts']:
        print('[{}/{}] populating {}...'.format(n, total, key), flush=True)
        deserialize_and_add_all(data[key], MODELS[key], n_threads)


def partition_dict_of_lists(data, max_chunk_size):
    n_divs = max(math.ceil(len(v)/max_chunk_size) for v in data.values())
    dct = {}
    for key, val in data.items():
        chunk_size = math.ceil(len(val)/n_divs)
        dct[key] = partition(val, chunk_size)
        dct[key].extend([] for __ in range(n_divs - len(dct[key])))
    subsets = [{k: dct[k][i] for k in dct.keys()} for i in range(n_divs)]
    return subsets


def populate_db(src_path, n_threads, max_chunk_size):
    with open(src_path) as f:
        data = json.load(f)

    with get_app().app_context():
        print('populating for env "{}"'.format(current_app.config['ENV']))
        subsets = partition_dict_of_lists(data, max_chunk_size)
        for i, subset in enumerate(subsets):
            populate(subset, i+1, len(subsets), n_threads)

    print('successfully populated.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--src_path',
        nargs='?',
        help='path to fake data JSON file (default={})'.format(DEF_SRC_PATH),
        default=DEF_SRC_PATH,
    )
    parser.add_argument(
        '--n_threads',
        help='number of threads to use in deserialization ({})'.format(
            DEF_N_THREADS),
        type=int,
        default=DEF_N_THREADS,
    )
    parser.add_argument(
        '--max_chunk_size',
        help='maximum chunk size to proccess at once in memory ({})'.format(
            DEF_MAX_CHUNK_SIZE),
        type=int,
        default=DEF_MAX_CHUNK_SIZE,
    )
    args = parser.parse_args()

    populate_db(
        src_path=args.src_path,
        n_threads=args.n_threads,
        max_chunk_size=args.max_chunk_size
    )


if __name__ == '__main__':
    main()
