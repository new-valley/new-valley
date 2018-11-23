from nv.database import db
from sqlalchemy.orm import validates
from marshmallow import ValidationError
import random

Column = db.Column
BigInteger = db.BigInteger
Integer = db.Integer
String = db.String
Text = db.Text
DateTime = db.DateTime
Table = db.Table
ForeignKey = db.ForeignKey
func = db.func
relationship = db.relationship
Table = db.Table

class Base(db.Model):
    __abstract__ = True

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def create_and_save(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj


def get_rand_id():
    return random.randint(0, 10**18)


class Avatar(Base):
    __tablename__ = 'avatars'
    avatar_id = Column(BigInteger, primary_key=True, default=get_rand_id)
    uri = Column(String(256), nullable=False)
    category = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    users = relationship('User', backref='avatar', lazy=True)


class User(Base):
    VALID_ROLES = {
        'user',
        'moderator',
        'admin',
    }

    VALID_STATUSES = {
        'active',
        'banned',
        'kicked',
    }

    MIN_UNHASHED_PASSWORD_LEN = 8

    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, default=get_rand_id)
    username = Column(String(128), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    roles = Column(String(256), nullable=False, default='user')
    status = Column(String(64), nullable=False, default='active')
    avatar_id = Column(
        BigInteger, ForeignKey('avatars.avatar_id'), nullable=True)
    signature = Column(String(1024), nullable=False, default='')
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    posts = relationship('Post', backref='user', lazy=True, cascade='delete')
    n_posts = Column(Integer, nullable=False, default=0)
    topics = relationship('Topic', backref='user', lazy=True, cascade='delete')
    n_topics = Column(Integer, nullable=False, default=0)


class Subforum(Base):
    __tablename__ = 'subforums'
    subforum_id = Column(BigInteger, primary_key=True, default=get_rand_id)
    title = Column(String(64), unique=True, nullable=False)
    description = Column(String(128), nullable=False)
    position = Column(Integer, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    topics = relationship(
        'Topic', backref='subforum', lazy=True, cascade='delete')


class Topic(Base):
    VALID_STATUSES = {
        'published',
        'unpublished',
        'locked',
    }

    __tablename__ = 'topics'

    topic_id = Column(BigInteger, primary_key=True, default=get_rand_id)
    title = Column(String(128), nullable=False)
    status = Column(String(64), nullable=False, default='published')
    user_id = Column(
        BigInteger, ForeignKey('users.user_id'), nullable=False)
    subforum_id = Column(
        BigInteger, ForeignKey('subforums.subforum_id'), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    posts = relationship('Post', backref='topic', lazy=True, cascade='delete')

    #implicitly checked in endpoints
    '''@validates('user_id')
    def check_user_exists(self, key, user_id):
        if not User.query.get(user_id):
            raise ValidationError('user id={} does not exist'.format(user_id))
        return user_id

    @validates('subforum_id')
    def check_subforum_exists(self, key, subforum_id):
        if not Subforum.query.get(subforum_id):
            raise ValidationError(
                'subforum id={} does not exist'.format(subforum_id))
        return subforum_id'''


class Post(Base):
    VALID_STATUSES = {
        'published',
        'unpublished',
    }

    __tablename__ = 'posts'

    post_id = Column(BigInteger, primary_key=True, default=get_rand_id)
    user_id = Column(
        BigInteger, ForeignKey('users.user_id'), nullable=False)
    topic_id = Column(
        BigInteger, ForeignKey('topics.topic_id'), nullable=False)
    content = Column(Text, nullable=False, default='')
    status = Column(String(64), nullable=False, default='published')
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())

    #implicitly checked in endpoints
    '''@validates('user_id')
    def check_user_exists(self, key, user_id):
        if not User.query.get(user_id):
            raise ValidationError('user id={} does not exist'.format(user_id))
        return user_id

    @validates('topic_id')
    def check_topic_exists(self, key, topic_id):
        if not Topic.query.get(topic_id):
            raise ValidationError(
                'topic id={} does not exist'.format(topic_id))
        return topic_id'''


class RevokedToken(Base):
    __tablename__ = 'revoked_tokens'
    revoked_token_id = Column(BigInteger, primary_key=True, default=get_rand_id)
    jti = Column(String(120))

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return query is not None
