import re  # 添加在文件顶部
from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash  # 错误模块
from peewee import MySQLDatabase, CharField, FloatField, IntegerField, Model  # 拼写错误

# 复用database.py的数据库配置
db = MySQLDatabase(
    "douban",
    host="localhost",
    port=3306,
    user="root",
    password="hlh9220416",
    charset='utf8mb4'
)

class Movie(Model):
    id = IntegerField()  # 添加主键字段
    title = CharField()
    year = CharField()
    class Meta:
        database = db
        table_name = 'douban_movie'

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET', 'POST'])
def search_movie():
    if request.method == 'POST':
        year = request.form.get('year')
        if not re.fullmatch(r'^\d{4}$', year):  # 改用fullmatch严格匹配
            return render_template('search_movie.html', error="请输入4位数字年份")
        movies = Movie.select().where(Movie.year == year)  # 精确匹配代替contains
        return render_template('search_result.html', 
                            movies=movies,
                            year=year)
    return render_template('search_movie.html')

@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('form.html')

@app.route('/signin', methods=['POST'])
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

if __name__ == '__main__':  # 修正单下划线错误
    db.connect()
    app.run(debug=True)