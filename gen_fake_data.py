#!/usr/bin/env python3

import random
from passlib.hash import pbkdf2_sha256 as sha256
import datetime as dt
import uuid
import json
import os


N_AVATARS = 100
N_USERS = 300
N_SUBFORUMS = 50
N_TOPICS = 150
N_POSTS = 500
DST_PATH = os.path.join('data', 'fake-data.json')

IMGS_URIS = [
    'http://forum.imguol.com/avatars/gallery/jogos/Enviados%20(45)/enviados2227.jpg',
    'http://forum.imguol.com/avatars/gallery/jogos/Enviados%20(55)/enviados2750.jpg',
    'http://forum.imguol.com/avatars/gallery/Xbox%20(6)/xb253.gif',
    'http://forum.imguol.com/avatars/gallery/esporte/Boteco2011%20(07)/boteco343.png',
]

USER_STATUSES = [
    'active',
    'banned',
    'kicked',
]

USER_ROLES = [
    'moderator',
    'user',
]

USERNAMES = [
    'fabio pancheri',
    'reptar',
    'argamassa',
    'Entei',
    'Jose Alves',
    'Estevão Trabalhos'
]

SIGNATURES = [
    'eu sou forca total',
    'ey b0ss',
    'ALOC MEY',
    'olar',
    'Eu sou aquele que percorre o caminho dos céus!',
]

TOPIC_TITLES = [
    'sujei meu dreamcast',
    'avalio usuarios',
    'macaco do vt',
    'panela de curitiba',
    'daew rapaziada',
    'AVALIEM MEU ENTEI',
    'MACACO DO VT :lol:',
]

SUBFORUM_TITLES = [
    'vale tudo',
    'vestibular',
    'papo cabeça',
    'entei',
    'games',
    'futebol',
]

SUBFORUM_DESCRIPTIONS = [
    'so Rapaziada boa',
    'games e g@t@s',
    'so os doido fi',
    'TOPZERA',
]

POST_CONTENTS = [
    'MP',
    'Deixem cair',
    'primeira',
    'monoestrela',
    'e msm eh',
    'cara o que eu fiz pra vc? nunca te deletei no msn. abraços',
]

TOPIC_STATUSES = [
    'published',
    'unpublished',
    'locked',
]

POST_STATUSES = [
    'published',
    'unpublished',
]

AVATAR_CATEGORIES = [
    'games',
    'enviados',
    'animados',
    'esportes',
    'jovem',
]

def generate_hash(password):
    return sha256.hash(password)

def sample(lst, n):
    return random.sample(lst, min(len(lst), n))

def choice(lst):
    return random.choice(lst)

def prob(p):
    return random.uniform(0, 1) <= p

def get_rand_str():
    return str(uuid.uuid4()).split('-')[-1]

def salt(min_size=6, max_size=10):
    size = random.randint(min_size, max_size)
    salt = get_rand_str()[:size]
    return salt

def get_rand_email():
    tail = random.randint(3, 10)
    email = '{}@{}.com'.format(get_rand_str(), get_rand_str()[:tail])
    return email

_IDS = set()
def get_rand_id():
    while True:
        uid = random.randint(0, 1000000)
        if not uid in _IDS:
            _IDS.add(uid)
            break
    return uid

def get_rand_datetime(start=None):
    if start is None:
        start = dt.datetime(2002, 1, 1)
    datetime = start + dt.timedelta(seconds=random.randint(0, 3*10**8))
    return datetime

def get_datetimes_pair():
    created = get_rand_datetime()
    updated = get_rand_datetime(created)
    return {
        'created_at': created.isoformat(),
        'updated_at': updated.isoformat(),
    }

def add_datetimes(dct):
    dct.update(get_datetimes_pair())
    return dct

def get_rand_avatar(**kwargs):
    dct = add_datetimes({
        'avatar_id': get_rand_id(),
        'uri': choice(IMGS_URIS),
        'category': choice(AVATAR_CATEGORIES),
    })
    dct.update(**kwargs)
    return dct

def get_rand_user(**kwargs):
    dct =  add_datetimes({
        'user_id': get_rand_id(),
        'username': choice(USERNAMES) + salt(),
        'roles': sample(USER_ROLES, random.randint(0, len(USER_ROLES))),
        'status': choice(USER_STATUSES),
        'avatar': get_rand_avatar(),
        'signature': choice(SIGNATURES) + prob(0.75)*salt(),
        'email': get_rand_email(),
        'password': generate_hash(get_rand_str()),
    })
    dct.update(**kwargs)
    return dct

def get_rand_subforum(**kwargs):
    dct = add_datetimes({
        'subforum_id': get_rand_id(),
        'title': choice(SUBFORUM_TITLES) + salt(),
        'description': choice(SUBFORUM_DESCRIPTIONS),
        'position': random.randint(0, 100),
    })
    dct.update(**kwargs)
    return dct

def get_rand_topic(**kwargs):
    dct = add_datetimes({
        'topic_id': get_rand_id(),
        'user': get_rand_user(),
        'title': choice(TOPIC_TITLES) + prob(0.75)*salt(),
        'status': choice(TOPIC_STATUSES),
        'subforum': get_rand_subforum(),
    })
    dct.update(**kwargs)
    return dct

def get_rand_post(**kwargs):
    dct = add_datetimes({
        'post_id': get_rand_id(),
        'user': get_rand_user(),
        'topic': get_rand_topic(),
        'content': choice(POST_CONTENTS) + prob(0.75)*salt(),
        'status': choice(POST_STATUSES),
    })
    dct.update(**kwargs)
    return dct

def get_fake_data():
    print('generating avatars...', flush=True, end=' ')
    avatars = [get_rand_avatar() for __ in range(N_AVATARS)]
    print('done')
    print('generating users...', flush=True, end=' ')
    users = [get_rand_user(avatar=choice(avatars)) for __ in range(N_USERS)]
    print('done')
    print('generating subforums...', flush=True, end=' ')
    subforums = [get_rand_subforum() for __ in range(N_SUBFORUMS)]
    print('done')
    print('generating topics...', flush=True, end=' ')
    topics = [get_rand_topic(user=choice(users), subforum=choice(subforums))\
        for __ in range(N_TOPICS)]
    print('done')
    print('generating posts...', flush=True, end=' ')
    posts = [get_rand_post(user=choice(users), topic=choice(topics))\
        for __ in range(N_POSTS)]
    print('done')
    data = {
        'avatars': avatars,
        'users': users,
        'subforums': subforums,
        'topics': topics,
        'posts': posts,
    }
    return data

def main():
    data = get_fake_data()
    with open(DST_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)
    print('saved generated data to "{}"'.format(DST_PATH))

if __name__ == '__main__':
    main()
