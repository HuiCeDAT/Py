'''
from flask import Flask
from flask_login import LoginManager
from .web import db

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    db.init_app(app)
    login_manager.init_app(app)
    
    return app
from .controllers import auth_bp, movie_bp
app.register_blueprint(auth_bp)
app.register_blueprint(movie_bp)

@login_manager.user_loader
def load_user(user_id):
    from .models.user import User
    return User.get_or_none(User.id == user_id)'''
