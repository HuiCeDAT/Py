
# 原错误导入：from extensions import db
from web.extensions import db  # 修正为绝对路径导入
# 原错误导入：from models.user import User
from web.models.user import User  # 修正为绝对路径导入
# 原错误导入：from models.movie import Movie, UserMovieCollect 
from web.models.movie import Movie, UserMovieCollect  # 修正为绝对路径导入