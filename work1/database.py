import requests
from bs4 import BeautifulSoup
from peewee import *
import time
import re

# 数据库配置
db = MySQLDatabase(
    "douban",  # 提前在MySQL中创建好数据库
    host="localhost",
    port=3306,
    user="root",
    password="hlh9220416",  # 修改为你的数据库密码
    charset='utf8mb4'
)

# 表结构实体
class Movie(Model):
    title = CharField(max_length=200)
    rating_num = FloatField()
    comment_num = IntegerField()
    directors = CharField(max_length=500)  # 增加长度
    actors = CharField(max_length=500)     # 增加长度
    year = CharField(max_length=50)        # 可能有多种格式
    country = CharField(max_length=200)
    category = CharField(max_length=200)
    pic = CharField(max_length=500)        # 长URL支持

    class Meta:
        database = db
        table_name = 'douban_movie'

# 创建表（如果不存在）
db.connect()
db.create_tables([Movie], safe=True)

# 请求头设置
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    'Referer': 'https://movie.douban.com/top250'
}

def fetch_page(url):
    """带重试机制的请求函数"""
    for _ in range(3):  # 重试3次
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败，状态码：{response.status_code}")
        except Exception as e:
            print(f"请求异常：{e}")
        time.sleep(2)  # 重试间隔
    return None

def parse_info(info_str):
    """解析年份/国家/类型信息"""
    info_parts = [part.strip() for part in info_str.split('/')]
    year = country = category = ''
    
    if info_parts:
        year = info_parts[0]
    if len(info_parts) > 1:
        # 处理可能有多个国家的情况
        country = ','.join([c for c in info_parts[1:] if not c.isdigit() and not re.search(r'\d', c)])
    if len(info_parts) > 2:
        # 处理类型信息
        category = ','.join([c for c in info_parts[2:] if c != country])
    
    return year, country, category

def extract_movie_data(movie):
    """提取单部电影数据"""
    try:
        # 标题
        title = movie.find('span', class_='title').get_text(strip=True)
    except:
        title = ''

    try:
        # 评分
        rating_num = float(movie.find('span', class_='rating_num').get_text(strip=True))
    except:
        rating_num = 0.0

    try:
        # 评价人数
        comment_str = movie.find('div', class_='star').find_all('span')[-1].get_text(strip=True)
        comment_num = int(re.search(r'\d+', comment_str).group())
    except:
        comment_num = 0

    try:
        # 导演和演员信息
        info = movie.find('div', class_='bd').find('p').get_text(strip=True)
        director_part = re.search(r'导演:(.*?)(主演:|$)', info)
        directors = director_part.group(1).strip() if director_part else ''
        
        actor_part = re.search(r'主演:(.*)', info)
        actors = actor_part.group(1).strip() if actor_part else ''
    except:
        directors = ''
        actors = ''

    try:
        # 年份/国家/类型
        info_text = movie.find('div', class_='bd').find('p').get_text(strip=True)
        info_line = re.split(r'\s+', info_text)[-1]  # 获取最后一行信息
        year, country, category = parse_info(info_line)
    except:
        year, country, category = '', '', ''

    try:
        # 图片链接
        pic = movie.find('img')['src']
    except:
        pic = ''

    return {
        'title': title,
        'rating_num': rating_num,
        'comment_num': comment_num,
        'directors': directors,
        'actors': actors,
        'year': year,
        'country': country,
        'category': category,
        'pic': pic
    }

def save_to_database(data):
    """保存数据到数据库"""
    try:
        # 避免重复插入
        if not Movie.select().where(
            (Movie.title == data['title']) &
            (Movie.year == data['year'])
        ).exists():
            Movie.create(**data)
    except Exception as e:
        print(f"数据库插入失败：{e}")

def main():
    base_url = 'https://movie.douban.com/top250'
    
    for page in range(0, 250, 25):  # 总共10页
        url = f"{base_url}?start={page}"
        print(f"正在爬取：{url}")
        
        html = fetch_page(url)
        if not html:
            continue
        
        soup = BeautifulSoup(html, 'lxml')
        movie_list = soup.find_all('div', class_='item')
        
        for movie in movie_list:
            movie_data = extract_movie_data(movie)
            save_to_database(movie_data)
        
        time.sleep(2)  

if __name__ == '__main__':
    main()
    db.close()
    print("数据爬取并存储完成！")