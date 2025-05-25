from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from web.services.movie_service import MovieService  # 修改导入路径
from web.models.movie import Movie  # 修改导入路径

movie_bp = Blueprint('movie', __name__, url_prefix='/movie')

@movie_bp.route('/list')
def movie_list():
    movies = Movie.query.all()  # SQLAlchemy query
    return render_template('movies/list.html', movies=movies)

@movie_bp.route('/collect/<int:movie_id>', methods=['POST'])
@login_required
def collect_movie(movie_id):
    success, msg = MovieService.collect_movie(current_user.id, movie_id)
    # 添加调试信息
    print(f"收藏状态: {success}, 消息: {msg}")
    if not success:
        flash(msg or '收藏失败', 'danger')
    else:
        flash('收藏成功', 'success')
    return redirect(request.referrer or url_for('movie.movie_list'))

@movie_bp.route('/uncollect/<int:movie_id>', methods=['POST'])
@login_required
def uncollect_movie(movie_id):
    success, msg = MovieService.uncollect_movie(current_user.id, movie_id)
    if not success:
        flash(msg or '取消收藏失败', 'danger')
    else:
        flash('已取消收藏', 'success')
    return redirect(request.referrer or url_for('movie.movie_list'))

@movie_bp.route('/mycollections')
@login_required
def my_collections():
    movies = MovieService.get_user_collections(current_user.id)
    return render_template('movies/mycollections.html', movies=movies)