"""
中国音乐数据爬取器
支持 QQ音乐、网易云音乐等平台
"""

import requests
import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict

def fetch_qq_music_data():
    """从QQ音乐爬取数据（演示版本）"""
    # 注：实际爬取需要处理反爬虫，这里使用演示数据
    print("[INFO] 正在生成QQ音乐演示数据...")

    songs = {
        '流行': [
            ('抱紧我', '张惠妹', 95),
            ('孤勇者', '陈奕迅', 98),
            ('好久不见', '五月天', 92),
            ('光年之外', '邓紫棋', 90),
            ('起风了', '买辣椒也用券', 94),
        ],
        '摇滚': [
            ('蜀国论剑', '李宗盛', 85),
            ('黑梦', '许巍', 88),
            ('晴天', '周杰伦', 91),
            ('别再闹了', '黑龙', 82),
            ('当爱已成往事', '赤色群晖', 84),
        ],
        '说唱': [
            ('Freestyle', 'GAI', 87),
            ('火焰', '周延', 86),
            ('光辉岁月', '大禾', 83),
            ('还要继续', 'Young G', 81),
            ('火拼', 'Vava', 85),
        ],
        '民族': [
            ('茉莉花', '邓丽君', 89),
            ('月满西楼', '李清照', 88),
            ('梁祝', '二胡协奏曲', 92),
            ('高山流水', '古琴', 91),
            ('十面埋伏', '琵琶', 90),
        ],
        '电子': [
            ('往后余生', 'MJ', 84),
            ('潮鸣', 'DJ', 86),
            ('未来的序曲', '电子', 85),
            ('星河渐暖', 'Synth', 87),
            ('冲破星辰', 'EDM', 88),
        ],
        '抒情': [
            ('一生有你', '无尽', 93),
            ('漂洋过海来看你', '琦琦', 94),
            ('我可能不会爱你', '五月天', 91),
            ('告白气球', '周杰伦', 92),
            ('七月上', '许魏洲', 90),
        ],
        '民谣': [
            ('成都', '赵雷', 95),
            ('理想', '赵雷', 93),
            ('南山南', '马頔', 91),
            ('烟火里的尘埃', '萧敬腾', 89),
            ('曾经的你', '许巍', 92),
        ],
    }

    data = []
    genres = list(songs.keys())

    # 为每个月生成数据
    for month in range(1, 13):
        for genre in genres:
            for idx, (title, artist, popularity) in enumerate(songs[genre]):
                # 每首歌的热度会随机波动
                popularity = max(50, min(100, popularity + (month - 6) * 2))

                data.append({
                    'month': month,
                    'genre': genre,
                    'song': title,
                    'artist': artist,
                    'popularity': popularity,
                    'rank': idx + 1,
                    'region': 'China'
                })

    return data

def fetch_netease_data():
    """从网易云音乐爬取数据（演示版本）"""
    print("[INFO] 正在生成网易云音乐演示数据...")

    # 可以从网易云音乐的公开API爬取
    # 这里为演示，返回空列表
    # 实际需要: https://music.163.com/

    return []

def generate_china_music_data():
    """生成中国音乐分析演示数据"""
    print("[INFO] 生成中国音乐分析数据...")

    qq_data = fetch_qq_music_data()

    # 保存为CSV
    filename = 'china_music_data.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['month', 'genre', 'song', 'artist', 'popularity', 'rank', 'region']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(qq_data)

    print("[OK] 中国音乐数据已生成: {}".format(filename))
    return qq_data

def get_china_genres_trend(data=None):
    """获取中国音乐各流派趋势"""
    if not data:
        try:
            with open('china_music_data.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        except:
            data = generate_china_music_data()

    trends = defaultdict(lambda: [0] * 12)

    for row in data:
        month = int(row['month'])
        genre = row['genre']
        popularity = int(row['popularity'])

        trends[genre][month - 1] = popularity

    return dict(trends)

def get_china_top_songs(month=None, genre=None):
    """获取中国音乐排行"""
    if not month:
        month = datetime.now().month

    try:
        with open('china_music_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except:
        data = generate_china_music_data()

    # 筛选
    filtered = [row for row in data if int(row['month']) == month]
    if genre:
        filtered = [row for row in filtered if row['genre'] == genre]

    # 排序
    filtered.sort(key=lambda x: int(x['popularity']), reverse=True)

    return filtered[:10]

def get_china_genre_stats():
    """获取各流派统计"""
    try:
        with open('china_music_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except:
        data = generate_china_music_data()

    stats = defaultdict(lambda: {'count': 0, 'avg_popularity': 0})

    for row in data:
        genre = row['genre']
        stats[genre]['count'] += 1
        stats[genre]['avg_popularity'] += int(row['popularity'])

    for genre in stats:
        if stats[genre]['count'] > 0:
            stats[genre]['avg_popularity'] /= stats[genre]['count']
            stats[genre]['avg_popularity'] = int(stats[genre]['avg_popularity'])

    return dict(stats)

if __name__ == '__main__':
    generate_china_music_data()
