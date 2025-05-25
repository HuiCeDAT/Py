import re  # 添加在文件顶部
from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from web.extensions import db, login_manager  # 统一使用绝对路径
from web.controllers.auth_controller import auth_bp
from web.controllers.movie_controller import movie_bp
from web.models.user import User

# 移除Peewee的数据库初始化（与Flask-SQLAlchemy冲突）
# db = MySQLDatabase(
#     "douban",
#     host="localhost",
#     port=3306,
#     user="root",
#     password="hlh9220416",
#     charset='utf8mb4'
# )

#from . import create_app
#app = create_app()

# 删除重复的Flask实例创建
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key'

# 初始化配置
# 删除以下错误导入 (line 24)
# from . import create_app

# 删除重复的Flask实例创建 (line 34-36)
app = Flask(__name__, template_folder=os.path.join('web', 'templates'))
app.config['SECRET_KEY'] = 'your-secret-key'

# 删除以下冲突的数据库连接管理 (Peewee残留)
# @app.before_request
# def before_request():
#     if db.is_closed():
#         db.connect()
# 
# @app.teardown_request
# def teardown_request(exc):
#     if not db.is_closed():
#         db.close()

@app.route('/')
def home():
    # 确认模板路径为 web/templates/home.html
    return render_template('home.html')  # 路径应匹配实际文件位置

# 确保存在有效的home路由
@app.route('/search', methods=['GET', 'POST'])
def search_movie():
    if request.method == 'POST':
        year = request.form.get('year')
        if not re.fullmatch(r'^\d{4}$', year):
            return render_template('search_movie.html', error="请输入4位数字年份")
        # 改为SQLAlchemy查询方式
        movies = Movie.query.filter_by(year=year).all()
        return render_template('search_result.html', 
                            movies=movies,
                            year=year)
    return render_template('search_movie.html')

@app.route('/signin', methods=['GET'])  # 移除 endpoint='auth.login'
def signin_form():
    return render_template('form.html')

@app.route('/signin', methods=['POST'], endpoint='auth.signin')
def signin():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return render_template('form.html',
                             message='用户名和密码不能为空',
                             username=username or '')
    
    if username == 'admin' and password == 'password':
        return render_template('signin-ok.html', username=username)
    
    return render_template('form.html',
                         message='用户名或密码错误',
                         username=username)

# 修改蓝图导入路径
# 在创建app实例后立即初始化扩展
init_app(app)  # 调用extensions.py中的初始化方法

# 注册蓝图前确保app已正确初始化
app.register_blueprint(auth_bp)
app.register_blueprint(movie_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # 改为SQLAlchemy查询方法

# 删除冲突的路由 (line 71-86)
# @app.route('/signin', methods=['POST'], endpoint='auth.signin')
# def signin():
#     ...

if __name__ == '__main__':
    app.run(debug=True)