"""
Simple WSGI app without Flask complexity
直接使用 WSGI，避免所有复杂依赖
"""

import csv
import json
from collections import defaultdict
import os

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
        print("[OK] Demo data generated")

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            DATA = list(reader)
            for row in DATA:
                row['year'] = int(row['year'])
                row['popularity'] = int(row['popularity'])
                row['rank'] = int(row['rank'])
        print("[OK] Loaded {} records".format(len(DATA)))
    except Exception as e:
        print("[ERROR] Cannot load data: {}".format(e))

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

    if path == '/' and method == 'GET':
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            body = f.read()
        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        return [body.encode('utf-8')]

    elif path == '/api/periods' and method == 'GET':
        data = get_periods()
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        return [body]

    elif path.startswith('/api/period/') and method == 'GET':
        try:
            year = int(path.split('/')[-1])
            data = get_period(year)
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            status = '200 OK'
            headers = [('Content-Type', 'application/json')]
            start_response(status, headers)
            return [body]
        except:
            status = '404 Not Found'
            start_response(status, [])
            return [b'Not Found']

    elif path == '/api/trends' and method == 'GET':
        data = get_trends()
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        return [body]

    elif path.startswith('/static/'):
        filepath = path[1:]  # 移除开头的 /
        try:
            with open(filepath, 'rb') as f:
                body = f.read()
            if filepath.endswith('.css'):
                content_type = 'text/css'
            elif filepath.endswith('.js'):
                content_type = 'application/javascript'
            else:
                content_type = 'application/octet-stream'
            status = '200 OK'
            headers = [('Content-Type', content_type)]
            start_response(status, headers)
            return [body]
        except:
            status = '404 Not Found'
            start_response(status, [])
            return [b'Not Found']

    else:
        status = '404 Not Found'
        start_response(status, [])
        return [b'Not Found']

# 兼容 Flask 名称
app = application

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('127.0.0.1', 5000, application)
    print('[OK] Server running on http://127.0.0.1:5000')
    server.serve_forever()
