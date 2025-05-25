from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from web.models.models import db, User, Movie, Collection, init_db
from web.services.auth_service import AuthService
from werkzeug.security import generate_password_hash, check_password_hash

# 创建Flask应用
app = Flask(__name__, template_folder='web/templates')
app.config['SECRET_KEY'] = 'your-secret-key-goes-here'

# 初始化Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return AuthService.get_user_by_id(int(user_id))

# 数据库连接管理
@app.before_request
def before_request():
    if db.is_closed():
        db.connect()

@app.teardown_request
def teardown_request(exc):
    if not db.is_closed():
        db.close()

# 路由定义
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('movie_list'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user, error = AuthService.login_user(username, password)
        if user:
            login_user(user)
            flash('登录成功！', 'success')
            next_url = request.args.get('next')
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('movie_list'))
        else:
            flash(error, 'danger')
            return render_template('form.html', username=username)
    
    return render_template('form.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('movie_list'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user, error = AuthService.register_user(username, password)
        if user:
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        else:
            flash(error, 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已成功登出', 'info')
    return redirect(url_for('login'))

@app.route('/movies')
def movie_list():
    movies = Movie.select()
    if current_user.is_authenticated:
        # 获取用户收藏的电影ID列表
        collected_movies = set(
            Collection.select(Collection.movie)
            .where(Collection.user == current_user.id)
            .tuples()
            .execute()
        )
        return render_template('movies/list.html', movies=movies, collected_movies=collected_movies)
    return render_template('movies/list.html', movies=movies, collected_movies=set())

@app.route('/movies/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.get_or_none(Movie.id == movie_id)
    if not movie:
        flash('电影不存在', 'danger')
        return redirect(url_for('movie_list'))
    return render_template('movies/detail.html', movie=movie)

@app.route('/collection/add/<int:movie_id>', methods=['POST'])
@login_required
def add_collection(movie_id):
    movie = Movie.get_or_none(Movie.id == movie_id)
    if not movie:
        return jsonify({'success': False, 'message': '电影不存在'})
    
    try:
        Collection.create(user=current_user.id, movie=movie_id)
        return jsonify({'success': True, 'message': '收藏成功'})
    except:
        return jsonify({'success': False, 'message': '已经收藏过了'})

@app.route('/collection/remove/<int:movie_id>', methods=['POST'])
@login_required
def remove_collection(movie_id):
    deleted = Collection.delete().where(
        (Collection.user == current_user.id) & 
        (Collection.movie == movie_id)
    ).execute()
    
    if deleted:
        return jsonify({'success': True, 'message': '取消收藏成功'})
    return jsonify({'success': False, 'message': '未找到收藏记录'})

@app.route('/my-collections')
@login_required
def my_collections():
    collections = (Movie
                  .select()
                  .join(Collection)
                  .where(Collection.user == current_user.id)
                  .order_by(Collection.created_at.desc()))
    return render_template('movies/mycollections.html', movies=collections)

if __name__ == '__main__':
    init_db()  # 初始化数据库表
    app.run(debug=True, host='0.0.0.0', port=5000)