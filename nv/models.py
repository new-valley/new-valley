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
Base = db.Model
Table = db.Table


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        return {
            'user_id': self.user_id,
            'username': str(self.username),
            'password': str(self.password),
        }

    @staticmethod
    def create_and_save(username, plain_password):
        new_user = User(username=username,
            password=generate_hash(plain_password))
        new_user.save()
        return new_user

class RevokedToken(Base):
    __tablename__ = 'revoked_tokens'
    revoked_token_id = Column(Integer, primary_key=True)
    jti = Column(String(120))

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return query is not None
