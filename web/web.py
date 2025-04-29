from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import MySQLDatabase, CharField, FloatField, IntegerField, Model

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
    id = IntegerField()
    name = CharField()
    year = IntegerField()
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
        movies = Movie.select().where(Movie.year.contains(year))
        return render_template('search_result.html', movies=movies)
    return render_template('search_movie.html')

@app.route('/signin', methods=['GET'])
def signin_form():
    return '''<form action="/signin" method="post">
              <p><input name="username"></p>
              <p><input name="password" type="password"></p>
              <p><button type="submit">Sign In</button></p>
              </form>'''

@app.route('/signin', methods=['POST'])
def signin():
    # 需要从request对象读取表单内容：
    if request.form['username']=='admin' and request.form['password']=='password':
        return '<h3>Hello, admin!</h3>'
    return '<h3>Bad username or password.</h3>'

if __name__ == '__main__':
    db.connect()
    app.run(debug=True)