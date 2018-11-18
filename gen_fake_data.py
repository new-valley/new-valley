#!/usr/bin/env python3


import argparse
import random
import datetime as dt
import uuid
import json
import os
import arrow


DEF_N_AVATARS = 100
DEF_N_USERS = 200
DEF_N_SUBFORUMS = 50
DEF_N_TOPICS = 150
DEF_N_POSTS = 500
DEF_DST_PATH = os.path.join('data', 'fake-data.json')
MIN_START_DATE = arrow.get(dt.datetime(1974, 1, 1)).datetime
MAX_TIMEDELTA = dt.timedelta(days=365*13)


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


def get_datetime(datetime):
    return arrow.get(datetime).datetime


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


def get_rand_id():
    return random.randint(0, 10**18)


def get_rand_datetime(start=MIN_START_DATE):
    start = get_datetime(start)
    max_delta = min(dt.datetime.now(dt.timezone.utc) - start, MAX_TIMEDELTA)
    delta_secs = random.randint(0, int(max_delta.total_seconds()))
    datetime = start + dt.timedelta(seconds=delta_secs)
    return datetime


def get_datetimes_pair(start=MIN_START_DATE):
    created = get_rand_datetime(start=start)
    updated = get_rand_datetime(created)
    return {
        'created_at': created.isoformat(),
        'updated_at': updated.isoformat(),
    }


def add_datetimes(dct, start=MIN_START_DATE):
    dct.update(get_datetimes_pair(start=start))
    return dct


def get_rand_avatar():
    dct = add_datetimes({
        'avatar_id': get_rand_id(),
        'uri': choice(IMGS_URIS),
        'category': choice(AVATAR_CATEGORIES),
    })
    return dct


def get_rand_user(avatar=None):
    avatar = get_rand_avatar() if avatar is None else avatar
    dct = add_datetimes({
        'user_id': get_rand_id(),
        'avatar_id': avatar['avatar_id'],
        'username': choice(USERNAMES) + salt(),
        'roles': ','.join(
            sample(USER_ROLES, random.randint(1, len(USER_ROLES)))),
        'status': choice(USER_STATUSES),
        'signature': choice(SIGNATURES) + prob(0.75)*salt(),
        'email': get_rand_email(),
        'password': get_rand_str(),
    }, start=avatar['created_at'])
    return dct


_POSITION = 0
def get_rand_subforum():
    global _POSITION
    _POSITION += random.randint(1, 100)
    dct = add_datetimes({
        'subforum_id': get_rand_id(),
        'title': choice(SUBFORUM_TITLES) + salt(),
        'description': choice(SUBFORUM_DESCRIPTIONS) + prob(0.25)*salt(),
        'position': _POSITION,
    })
    return dct


def get_rand_topic(user=None, subforum=None):
    user = get_rand_user() if user is None else user
    subforum = get_rand_subforum() if subforum is None else subforum
    dct = add_datetimes({
        'topic_id': get_rand_id(),
        'user_id': user['user_id'],
        'subforum_id': subforum['subforum_id'],
        'title': choice(TOPIC_TITLES) + prob(0.75)*salt(),
        'status': choice(TOPIC_STATUSES),
    }, start=max(user['created_at'], subforum['created_at']))
    return dct


def get_rand_post(user=None, topic=None):
    user = get_rand_user() if user is None else user
    topic = get_rand_topic() if topic is None else topic
    dct = add_datetimes({
        'post_id': get_rand_id(),
        'user_id': user['user_id'],
        'topic_id': topic['topic_id'],
        'content': choice(POST_CONTENTS) + prob(0.75)*salt(),
        'status': choice(POST_STATUSES),
    }, start=max(user['created_at'], topic['created_at']))
    return dct


def gen_fake_data(n_avatars, n_users, n_subforums, n_topics, n_posts, dst_path):
    print('generating avatars...', flush=True, end=' ')
    avatars = [get_rand_avatar() for __ in range(n_avatars)]
    print('done')
    print('generating users...', flush=True, end=' ')
    users = [get_rand_user(avatar=choice(avatars)) for __ in range(n_users)]
    print('done')
    print('generating subforums...', flush=True, end=' ')
    subforums = [get_rand_subforum() for __ in range(n_subforums)]
    print('done')
    print('generating topics...', flush=True, end=' ')
    topics = [get_rand_topic(user=choice(users), subforum=choice(subforums))\
        for __ in range(n_topics)]
    print('done')
    print('generating posts...', flush=True, end=' ')
    posts = [get_rand_post(user=choice(users), topic=choice(topics))\
        for __ in range(n_posts)]
    print('done')
    data = {
        'avatars': avatars,
        'users': users,
        'subforums': subforums,
        'topics': topics,
        'posts': posts,
    }
    with open(dst_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)
    print('saved generated data to "{}"'.format(dst_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dst_path',
        nargs='?',
        help='path to save result JSON file (default={})'.format(DEF_DST_PATH),
        default=DEF_DST_PATH,
    )
    parser.add_argument(
        '--n_avatars',
        help='number of avatars to generate ({})'.format(DEF_N_AVATARS),
        type=int,
        default=DEF_N_AVATARS,
    )
    parser.add_argument(
        '--n_users',
        help='number of users to generate ({})'.format(DEF_N_USERS),
        type=int,
        default=DEF_N_USERS,
    )
    parser.add_argument(
        '--n_subforums',
        help='number of subforums to generate ({})'.format(
            DEF_N_SUBFORUMS),
        type=int,
        default=DEF_N_SUBFORUMS,
    )
    parser.add_argument(
        '--n_topics',
        help='number of topics to generate ({})'.format(DEF_N_TOPICS),
        type=int,
        default=DEF_N_TOPICS,
    )
    parser.add_argument(
        '--n_posts',
        help='number of posts to generate ({})'.format(DEF_N_POSTS),
        type=int,
        default=DEF_N_POSTS,
    )
    args = parser.parse_args()

    gen_fake_data(
        n_avatars=args.n_avatars,
        n_users=args.n_users,
        n_subforums=args.n_subforums,
        n_topics=args.n_topics,
        n_posts=args.n_posts,
        dst_path=args.dst_path,
    )


if __name__ == '__main__':
    main()
