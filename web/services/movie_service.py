from web.models.movie import Movie, UserMovieCollect  # 修复导入路径
from web.models.user import User
from peewee import DoesNotExist

class MovieService:
    @staticmethod
    def collect_movie(user_id, movie_id):
        # 改为SQLAlchemy查询方式
        user = User.query.get(user_id)
        movie = Movie.query.get(movie_id)
        if not user or not movie:
            return False, "用户或电影不存在"
        # 改为SQLAlchemy存在性检查
        if UserMovieCollect.query.filter_by(user_id=user_id, movie_id=movie_id).first():
            return False, "已收藏"
        new_collect = UserMovieCollect(user_id=user_id, movie_id=movie_id)
        db.session.add(new_collect)
        db.session.commit()
        return True, None

    @staticmethod
    def uncollect_movie(user_id, movie_id):
        collect = UserMovieCollect.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if collect:
            db.session.delete(collect)
            db.session.commit()
            return True, None
        return False, "未收藏"

    @staticmethod
    def get_user_collections(user_id):
        # 改为SQLAlchemy关联查询
        return Movie.query.join(UserMovieCollect).filter(UserMovieCollect.user_id == user_id).all()

    @staticmethod
    def is_collected(user_id, movie_id):
        # 改为SQLAlchemy查询方式
        return UserMovieCollect.query.filter_by(
            user_id=user_id, 
            movie_id=movie_id
        ).first() is not None