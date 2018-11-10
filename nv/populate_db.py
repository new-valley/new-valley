#!/usr/bin/env python3


from nv import app, config
from nv.models import Avatar, User, Subforum, Post, Topic
from nv.serializers import (
    AvatarSchema,
    UserSchema,
    SubforumSchema,
    PostSchema,
    TopicSchema
)
from nv.database import db
import os

import json
import random

FAKE_DATA_PATH = os.path.join('data', 'fake-data.json')

def get_app(**conf):
    return app.get_app(**conf)

def populate(schema, data):
    with get_app().app_context():
        objs = schema.load(data)
        db.session.add_all(objs)
        db.session.commit()

def populate_avatars(data):
    populate(AvatarSchema(many=True), data['avatars'])

def populate_users(data):
    with get_app().app_context():
        avatars = Avatar.query.all()
    users = data['users']
    for user in users:
        del user['avatar']
        user['avatar_id'] = random.choice(avatars).avatar_id
    populate(UserSchema(many=True), users)

def populate_subforums(data):
    populate(SubforumSchema(many=True), data['subforums'])

def populate_topics(data):
    with get_app().app_context():
        subforums = Subforum.query.all()
    topics = data['topics']
    for topic in topics:
        del topic['subforum']
        topic['subforum_id'] = random.choice(subforums).subforum_id
    populate(TopicSchema(many=True), topics)

def populate_posts(data):
    with get_app().app_context():
        topics = Topic.query.all()
        users = User.query.all()
    posts = data['posts']
    for post in posts:
        del post['user']
        del post['topic']
        post['user_id'] = random.choice(users).user_id
        post['topic_id'] = random.choice(topics).topic_id
    populate(PostSchema(many=True), posts)

def populate_db(data):
    print('populating avatars...', flush=True, end=' ')
    populate_avatars(data)
    print('done')
    print('populating users...', flush=True, end=' ')
    populate_users(data)
    print('done')
    print('populating subforums...', flush=True, end=' ')
    populate_subforums(data)
    print('done')
    print('populating topics...', flush=True, end=' ')
    populate_topics(data)
    print('done')
    print('populating posts...', flush=True, end=' ')
    populate_posts(data)
    print('done')
    return

def main():
    with open(FAKE_DATA_PATH) as f:
        data = json.load(f)
    populate_db(data)

if __name__ == '__main__':
    main()
