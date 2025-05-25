from web.extensions import db
from web.models.user import User
from web.models.movie import Movie, UserMovieCollect

def init_db():
    with app.app_context():  # 需要Flask应用上下文
        db.create_all()  # SQLAlchemy自动创建所有模型对应的表
    print("数据库表已创建/已存在。")

if __name__ == '__main__':
    from web.web import app  # 导入Flask应用实例
    init_db()