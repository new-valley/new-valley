from nv.database import db
from nv.util import generate_hash

Column = db.Column
Integer = db.Integer
String = db.String
Text = db.Text
DateTime = db.DateTime
Table = db.Table
ForeignKey = db.ForeignKey
func = db.func
relationship = db.relationship
#Base = db.Model
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


class Avatar(Base):
    __tablename__ = 'avatars'
    avatar_id = Column(Integer, primary_key=True)
    uri = Column(String(256), nullable=False)
    category = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    users = relationship('User', backref='avatar', lazy=True)


USER_STATUSES = {
    'active',
    'banned',
    'kicked',
}

USER_ROLES = {
    'user',
    'moderator',
}

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    roles = Column(String(256), nullable=False, default='user')
    status = Column(String(64), nullable=False, default='active')
    avatar_id = Column(
        Integer, ForeignKey('avatars.avatar_id'), nullable=False)
    signature = Column(String(1024), nullable=False, default='')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    posts = relationship('Post', backref='user', lazy=True, cascade='delete')

    def __init__(self, **kwargs):
        kwargs['password'] = generate_hash(kwargs['password'])
        super().__init__(**kwargs)


class Subforum(Base):
    __tablename__ = 'subforums'
    subforum_id = Column(Integer, primary_key=True)
    title = Column(String(64), unique=True, nullable=False)
    description = Column(String(128), nullable=False)
    position = Column(Integer, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    topics = relationship(
        'Topic', backref='subforum', lazy=True, cascade='delete')


TOPIC_STATUSES = {
    'published',
    'unpublished',
    'locked',
}

class Topic(Base):
    __tablename__ = 'topics'
    topic_id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    status = Column(String(64), nullable=False, default='published')
    subforum_id = Column(
        Integer, ForeignKey('subforums.subforum_id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    posts = relationship('Post', backref='topic', lazy=True, cascade='delete')


POST_STATUSES = {
    'published',
    'unpublished',
}

class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('users.user_id'), nullable=False)
    topic_id = Column(
        Integer, ForeignKey('topics.topic_id'), nullable=False)
    content = Column(Text, nullable=False, default='')
    status = Column(String(64), nullable=False, default='published')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RevokedToken(Base):
    __tablename__ = 'revoked_tokens'
    revoked_token_id = Column(Integer, primary_key=True)
    jti = Column(String(120))

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return query is not None
