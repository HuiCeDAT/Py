import requests
from bs4 import BeautifulSoup
from peewee import *
import time
import re



# ------------------ 数据库配置 ------------------
db = MySQLDatabase(
    "douban",
    host="localhost",
    port=3306,
    user="root",
    password="hlh9220416",  # 修改为你的数据库密码
    charset='utf8mb4'
)


# # 测试数据库连接
# try:
#     db.connect()
#     print("数据库连接成功！")
#     db.close()
# except Exception as e:
#     print(f"数据库连接失败：{e}")


class Movie(Model):
    title = CharField(max_length=200)
    rating_num = FloatField()
    directors = CharField(max_length=500)
    actors = CharField(max_length=500)
    year = CharField(max_length=50)
    country = CharField(max_length=200)
    category = CharField(max_length=200)
    pic = CharField(max_length=500)

    class Meta:
        database = db
        table_name = 'douban_movie'

# 强制重建表结构（开发环境使用）
def init_database():
    db.connect()
    db.drop_tables([Movie], safe=True)
    db.create_tables([Movie])
    print("数据库表已重建")

# ------------------ 爬虫配置 ------------------
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    'Referer': 'https://movie.douban.com/top250'
}

def fetch_page(url):
    """带重试机制的请求函数"""
    for retry in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            print(f"请求失败，状态码：{response.status_code} (第{retry+1}次重试)")
        except Exception as e:
            print(f"请求异常：{str(e)[:50]}... (第{retry+1}次重试)")
        time.sleep(2)
    return None

def parse_info(info_str):
    # 修复函数结构（原函数存在提前返回问题）
    # 扩展国家关键词列表
    country_keywords = [
        '中国大陆', '美国', '香港', '日本', '韩国', '英国', '法国', '台湾', '意大利', '德国',
        '加拿大', '澳大利亚', '俄罗斯', '印度', '泰国', '西班牙', '巴西', '墨西哥', '瑞典', '丹麦'
    ]
    
    # 年份提取（增强正则匹配）
    year_match = re.search(r'(?:^|\D)((?:19|20)\d{2})(?:\D|$)', info_str)
    year = year_match.group(1) if year_match else ''
    
    # 国家识别（处理复合名称）
    country_parts = []
    for part in re.split(r'[/／\s·　　|，、;；]', info_str):
        part = re.sub(r'[（）()]', '', part).strip()
        if any(kw in part for kw in country_keywords):
            country_parts.append(part.replace('西德', '德国').replace('北韩', '韩国'))
    
    # 类型识别（优化过滤条件）
    category_blacklist = country_keywords + ['分钟', '上映', '首播', '集数']
    category_parts = [
        p.strip() for p in re.split(r'[/／]', info_str)
        if p.strip() and p.strip() not in category_blacklist
        and 2 <= len(p.strip()) <= 6
    ]
    
    return (
        year[:4] if year else '',
        ', '.join(sorted(set(country_parts)))[:200],
        ', '.join(sorted(set(category_parts)))[:200]
    )

def extract_movie_data(movie):
    """提取单部电影数据（增强版）"""
    data = {
        'title': '',
        'rating_num': 0.0,
        'directors': '',
        'actors': '',
        'year': '',
        'country': '',
        'category': '',
        'pic': ''
    }

    try:
        # 处理多语言标题情况
        title_tags = movie.find_all('span', class_='title')
        if title_tags:
            # 允许中文、数字、中英文标点和空格
            allowed_chars = r'\u4e00-\u9fa50-9，。！？、；：“”‘’《》【】（）—～…:：\s'
            data['title'] = next(
                (tag.get_text(strip=True) for tag in title_tags 
                 if re.match(f'^[{allowed_chars}]+$', tag.text)),
                title_tags[0].get_text(strip=True)  # 保底取第一个标题
            )
        else:
            # 备选标题提取方式
            alt_title = movie.find('span', class_='other')
            data['title'] = alt_title.get_text(strip=True) if alt_title else ''
    except Exception as e:
        print(f"标题解析失败：{str(e)[:50]}")

    try:
        # 评分（处理格式异常）
        rating_tag = movie.find('span', class_='rating_num')
        data['rating_num'] = float(rating_tag.text) if rating_tag else 0.0
    except ValueError:
        data['rating_num'] = 0.0

    # try:
    #     comment_tag = movie.find('div', class_='star').find_all('span')[-1]
    #     comment_str = comment_tag.text if comment_tag else ''
    #     data['comment_num'] = int(re.search(r'\d+', comment_str).group()) if comment_str else 0
    # except Exception as e:
    #     print(f"评论数解析失败：{str(e)[:50]}")

    try:
        # 导演和演员信息
        info_tag = movie.find('div', class_='bd').find('p')
        info_text = info_tag.get_text(" ", strip=True)  # 保留换行信息
        
        # 导演解析（支持多导演）
        director_match = re.search(r'导演:\s*(.*?)(?=\s*/|\s*主|$)', info_text)
        if director_match:
            directors = re.split(r'[/／\s]+', director_match.group(1).strip())
            data['directors'] = ', '.join([d.strip() for d in directors if d.strip()])[:500]
        
        # 演员解析（支持多分隔符）
        actor_match = re.search(r'主演:\s*(.*?)(?=\s*/|$)', info_text)
        if actor_match:
            actors = re.split(r'[/／、\s]+', actor_match.group(1).strip())
            data['actors'] = ', '.join([a.strip() for a in actors if a.strip()])[:500]
    except Exception as e:
        print(f"人员信息解析失败：{str(e)[:50]}")

    try:
        # 年份/国家/类型
        # 改进信息行提取方式
        info_lines = info_tag.get_text(" ", strip=True).split('\n')
        # 寻找包含年份的最后有效行
        info_line = next(
            (line.strip() for line in reversed(info_lines) 
            if re.search(r'(?:19|20)\d{2}', line)),
            ''
        )
        if not info_line:
            info_line = info_tag.get_text(" ", strip=True).split('...')[-1]
            
        year, country, category = parse_info(info_line)
        data.update({
            'year': year or '未知年份',
            'country': country or '未知地区',
            'category': category or '未分类'
        })
    except Exception as e:
        print(f"基础信息解析失败：{str(e)[:50]}")

    try:
        # 图片链接（处理相对路径）
        img_tag = movie.find('img')
        data['pic'] = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ''
        if data['pic'].startswith('//'):
            data['pic'] = 'https:' + data['pic']
    except Exception as e:
        print(f"图片解析失败：{str(e)[:50]}")

    return data

def save_to_database(data):
    """带字段校验的数据保存"""
    try:
        for field in ['directors', 'actors', 'country', 'category']:
            data[field] = data.get(field, '')[:Movie._meta.fields[field].max_length]
        
        # 去重检查
        if not Movie.select().where(
            (Movie.title == data['title']) &
            (Movie.year == data['year'])
        ).exists():
            Movie.create(**data)
            print(f"已保存：{data['title']}")
        else:
            print(f"已存在：{data['title']}")
            
    except Exception as e:
        print(f"数据库操作失败：{str(e)[:100]}")
        print(f"问题数据：{ {k:v[:50] for k,v in data.items()} }")

def main():
    init_database()  # 初始化数据库
    
    for page in range(0, 250, 25):
        url = f"https://movie.douban.com/top250?start={page}"
        print(f"\n正在爬取：{url}")
        
        html = fetch_page(url)
        if not html:
            continue
            
        soup = BeautifulSoup(html, 'lxml')
        for movie in soup.find_all('div', class_='item'):
            movie_data = extract_movie_data(movie)
            print(f"正在处理：{movie_data['title']}")
            save_to_database(movie_data)
        
        time.sleep(1.5)  # 增加爬取间隔

if __name__ == '__main__':
    main()
    db.close()
    print("\n数据爬取并存储完成！")