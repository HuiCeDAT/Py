from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from web.services.auth_service import AuthService
from urllib.parse import urlparse, urljoin

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('movie.movie_list'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user, error = AuthService.login_user(username, password)
        if user:
            login_user(user)
            flash('登录成功', 'success')
            next_url = request.args.get('next')
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return render_template('signin-ok.html', username=user.username)
        else:
            return render_template('form.html', message=error, username=username)
    return render_template('form.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('movie.movie_list'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user, error = AuthService.register_user(username, password)
        if user:
            flash('注册成功，请登录', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(error, 'danger')
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('auth.login'))