from flask import Flask, render_template, jsonify
import csv
import json
from collections import defaultdict

app = Flask(__name__)

# 全局变量存储数据
DATA = []

def load_data():
    """加载处理好的数据"""
    global DATA
    import os

    # 如果数据文件不存在，自动生成
    csv_path = 'processed_data.csv'
    if not os.path.exists(csv_path):
        print("[INFO] Data file not found. Generating demo data...")
        try:
            # 直接导入并运行生成函数
            from generate_demo import generate_demo_data
            data = generate_demo_data()
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            print("[OK] Demo data generated")
        except Exception as e:
            print("[ERROR] Failed to generate demo data: {}".format(e))

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            DATA = list(reader)
            # 转换数据类型
            for row in DATA:
                row['year'] = int(row['year'])
                row['popularity'] = int(row['popularity'])
                row['rank'] = int(row['rank'])
        print("[OK] Loaded {} records".format(len(DATA)))
    except Exception as e:
        print("[ERROR] Cannot load data: {}".format(e))

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/periods')
def get_periods():
    """获取所有5年周期的数据"""
    periods = {}
    years = [1995, 2000, 2005, 2010, 2015, 2020]

    for year in years:
        # 获取该年份周期的数据（当年 ± 2年）
        period_data = [d for d in DATA if abs(int(d['year']) - year) <= 2]

        if not period_data:
            continue

        # 统计流派
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

        # 排序流派，取前5个
        sorted_genres = sorted(
            genre_stats.items(),
            key=lambda x: (x[1]['popularity'] / max(x[1]['count'], 1)),
            reverse=True
        )[:5]

        period_data_dict = {
            'year': year,
            'period': f'{year-2}-{year+2}',
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

        periods[f'period_{year}'] = period_data_dict

    return jsonify(periods)

@app.route('/api/period/<int:year>')
def get_period(year):
    """获取特定年份的详细数据"""
    # 获取该年份的前10首歌
    year_data = [d for d in DATA if int(d['year']) == year]
    year_data.sort(key=lambda x: int(x['popularity']), reverse=True)

    top_10 = year_data[:10]

    # 流派统计
    genre_stats = defaultdict(int)
    for entry in year_data:
        genre_stats[entry['genre']] += 1

    top_genres = sorted(genre_stats.items(), key=lambda x: x[1], reverse=True)[:5]

    return jsonify({
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
            {
                'name': genre,
                'count': count
            }
            for genre, count in top_genres
        ]
    })

@app.route('/api/trends')
def get_trends():
    """获取流派趋势数据（按年份）"""
    trends = defaultdict(lambda: defaultdict(int))

    for entry in DATA:
        year = int(entry['year'])
        genre = entry['genre']
        trends[genre][year] += 1

    # 5个主要流派的趋势
    main_genres = ['pop', 'rock', 'hip-hop', 'electronic', 'r&b']
    result = {}

    for genre in main_genres:
        years = sorted(trends[genre].keys())
        result[genre] = {
            'label': genre.upper(),
            'data': [trends[genre].get(y, 0) for y in range(1995, 2021)]
        }

    return jsonify(result)

if __name__ == '__main__':
    load_data()
    app.run(debug=True, port=5000)
