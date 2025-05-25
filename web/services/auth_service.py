from web.models.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def register_user(username, password):
        try:
            with db.atomic():
                # 检查用户是否存在
                if User.select().where(User.username == username).exists():
                    return None, "用户名已存在"
                
                # 创建新用户
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                logger.debug(f"Registering user {username} with hashed password: {hashed_password}")
                user = User.create(
                    username=username,
                    password=hashed_password
                )
                return user, None
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return None, str(e)

    @staticmethod
    def login_user(username, password):
        try:
            user = User.get_or_none(User.username == username)
            logger.debug(f"Login attempt for user {username}")
            logger.debug(f"User found: {user is not None}")
            if user:
                logger.debug(f"Stored hashed password: {user.password}")
                logger.debug(f"Checking password hash...")
                if check_password_hash(user.password, password):
                    logger.debug("Password check successful")
                    return user, None
                logger.debug("Password check failed")
            return None, "用户名或密码错误"
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return None, str(e)

    @staticmethod
    def get_user_by_id(user_id):
        return User.get_or_none(User.id == user_id)