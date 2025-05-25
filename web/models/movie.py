from web.extensions import db
from datetime import datetime

class Movie(db.Model):
    __tablename__ = 'douban_movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    year = db.Column(db.String(10))
    pic = db.Column(db.String(500), nullable=True)
    
    # 添加关系定义
    collectors = db.relationship('UserMovieCollect', back_populates='movie')

    def __str__(self):
        return f"{self.title}({self.year})"

class UserMovieCollect(db.Model):
    __tablename__ = 'user_movie_collect'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('douban_movie.id'))
    collect_time = db.Column(db.DateTime, default=datetime.now)
    
    # 定义双向关系
    user = db.relationship('User', back_populates='collections')
    movie = db.relationship('Movie', back_populates='collectors')

    def __str__(self):
        return f"{self.user} 收藏了 {self.movie} 于 {self.collect_time}"