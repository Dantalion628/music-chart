"""
最简单的 WSGI 应用 - 只用标准库
"""

import csv
import json
import os
from collections import defaultdict

# 全局数据
DATA = []

def load_data():
    """加载或生成数据"""
    global DATA
    csv_path = 'processed_data.csv'

    if not os.path.exists(csv_path):
        from generate_demo import generate_demo_data
        data = generate_demo_data()
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            DATA = list(reader)
            for row in DATA:
                row['year'] = int(row['year'])
                row['popularity'] = int(row['popularity'])
                row['rank'] = int(row['rank'])
    except Exception as e:
        print("Error loading data: {}".format(e))

def read_file(filepath):
    """读取文件内容"""
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except:
        return None

def get_content_type(filepath):
    """获取文件的Content-Type"""
    if filepath.endswith('.css'):
        return 'text/css; charset=utf-8'
    elif filepath.endswith('.js'):
        return 'application/javascript; charset=utf-8'
    elif filepath.endswith('.json'):
        return 'application/json'
    elif filepath.endswith('.html'):
        return 'text/html; charset=utf-8'
    elif filepath.endswith('.png'):
        return 'image/png'
    elif filepath.endswith('.jpg') or filepath.endswith('.jpeg'):
        return 'image/jpeg'
    else:
        return 'application/octet-stream'

def get_periods():
    """获取5年周期数据"""
    periods = {}
    years = [1995, 2000, 2005, 2010, 2015, 2020]

    for year in years:
        period_data = [d for d in DATA if abs(int(d['year']) - year) <= 2]
        if not period_data:
            continue

        genre_stats = defaultdict(lambda: {'count': 0, 'popularity': 0, 'songs': []})
        for entry in period_data:
            genre = entry['genre']
            genre_stats[genre]['count'] += 1
            genre_stats[genre]['popularity'] += int(entry['popularity'])
            if len(genre_stats[genre]['songs']) < 3:
                genre_stats[genre]['songs'].append({
                    'song': entry['song'],
                    'artist': entry['artist'],
                    'popularity': int(entry['popularity'])
                })

        sorted_genres = sorted(
            genre_stats.items(),
            key=lambda x: (x[1]['popularity'] / max(x[1]['count'], 1)),
            reverse=True
        )[:5]

        periods['period_{}'.format(year)] = {
            'year': year,
            'period': '{}-{}'.format(year-2, year+2),
            'genres': [
                {
                    'name': name,
                    'count': stats['count'],
                    'popularity': stats['popularity'] // max(stats['count'], 1),
                    'sample_songs': stats['songs']
                }
                for name, stats in sorted_genres
            ]
        }

    return periods

def get_period(year):
    """获取特定年份的数据"""
    year_data = [d for d in DATA if int(d['year']) == year]
    year_data.sort(key=lambda x: int(x['popularity']), reverse=True)
    top_10 = year_data[:10]

    genre_stats = defaultdict(int)
    for entry in year_data:
        genre_stats[entry['genre']] += 1

    top_genres = sorted(genre_stats.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        'year': year,
        'top_10_songs': [
            {
                'rank': i + 1,
                'song': d['song'],
                'artist': d['artist'],
                'genre': d['genre'],
                'popularity': int(d['popularity'])
            }
            for i, d in enumerate(top_10)
        ],
        'top_5_genres': [
            {'name': genre, 'count': count}
            for genre, count in top_genres
        ]
    }

def get_trends():
    """获取流派趋势"""
    trends = defaultdict(lambda: defaultdict(int))
    for entry in DATA:
        year = int(entry['year'])
        genre = entry['genre']
        trends[genre][year] += 1

    main_genres = ['pop', 'rock', 'hip-hop', 'electronic', 'r&b']
    result = {}
    for genre in main_genres:
        result[genre] = {
            'label': genre.upper(),
            'data': [trends[genre].get(y, 0) for y in range(1995, 2021)]
        }
    return result

# 加载数据
load_data()

# WSGI 应用
def application(environ, start_response):
    """WSGI 应用入口"""
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')

    try:
        # 主页（首页封面）
        if path == '/' and method == 'GET':
            body = read_file('templates/landing.html')
            if body:
                start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                return [body]

        # 应用页面
        elif path == '/app' and method == 'GET':
            body = read_file('templates/app.html')
            if body:
                start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                return [body]

        # API: 5年周期
        elif path == '/api/periods' and method == 'GET':
            data = get_periods()
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [body]

        # API: 特定年份
        elif path.startswith('/api/period/') and method == 'GET':
            try:
                year = int(path.split('/')[-1])
                data = get_period(year)
                body = json.dumps(data, ensure_ascii=False).encode('utf-8')
                start_response('200 OK', [('Content-Type', 'application/json')])
                return [body]
            except:
                start_response('404 Not Found', [])
                return [b'Not Found']

        # API: 流派趋势
        elif path == '/api/trends' and method == 'GET':
            data = get_trends()
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [body]

        # 静态文件
        elif path.startswith('/static/'):
            filepath = path[1:]
            body = read_file(filepath)
            if body:
                content_type = get_content_type(filepath)
                start_response('200 OK', [('Content-Type', content_type)])
                return [body]
            else:
                start_response('404 Not Found', [])
                return [b'Not Found']

        # 其他路由 404
        else:
            start_response('404 Not Found', [])
            return [b'Not Found']

    except Exception as e:
        print("Error: {}".format(e))
        start_response('500 Internal Server Error', [])
        return [b'Internal Server Error']

# 兼容 gunicorn
app = application

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    print('Starting server on http://127.0.0.1:5000')
    server = make_server('127.0.0.1', 5000, application)
    server.serve_forever()
