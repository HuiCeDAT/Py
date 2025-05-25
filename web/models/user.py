from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from web.extensions import db  # 正确导入

class User(UserMixin, db.Model):  # 改为继承db.Model
    id = db.Column(db.Integer, primary_key=True)  # 使用SQLAlchemy字段类型
    username = db.Column(db.String(40), unique=True)
    password_hash = db.Column(db.String(128))
    # 添加与UserMovieCollect的反向关系
    collections = db.relationship('UserMovieCollect', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    def __str__(self):
        return self.username