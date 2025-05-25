from peewee import *
from flask_login import UserMixin
from datetime import datetime

# 使用已有的数据库连接
db = MySQLDatabase(
    "douban",
    host="localhost",
    port=3306,
    user="root",
    password="hlh9220416",
    charset='utf8mb4'
)

class BaseModel(Model):
    class Meta:
        database = db

class User(UserMixin, BaseModel):
    id = AutoField()
    username = CharField(unique=True, max_length=80)
    password = CharField(max_length=255)  # 增加长度以存储哈希值
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'users'

class Movie(BaseModel):
    id = AutoField()
    title = CharField(max_length=200)
    rating_num = FloatField()
    directors = CharField(max_length=500)
    actors = CharField(max_length=500)
    year = CharField(max_length=50)
    country = CharField(max_length=200)
    category = CharField(max_length=200)
    pic = CharField(max_length=500)

    class Meta:
        table_name = 'douban_movie'

class Collection(BaseModel):
    user = ForeignKeyField(User, backref='collections')
    movie = ForeignKeyField(Movie, backref='collected_by')
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'collections'
        indexes = (
            (('user', 'movie'), True),  # 确保用户不会重复收藏同一部电影
        )

def init_db():
    db.connect()
    # 删除旧表并重新创建
    db.drop_tables([User, Collection])
    db.create_tables([User, Collection])
    print("数据库表已创建") 