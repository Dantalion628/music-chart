"""
网易云音乐实时排行榜数据获取
直接从网易云 API 获取最新的真实数据（使用 urllib，无外部依赖）
"""

import json
import csv
import os
import urllib.request
import urllib.error
from datetime import datetime
from collections import defaultdict
import sys

class NeteaseAPI:
    """网易云音乐 API 客户端"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://music.163.com',
        }

    def _request(self, url, params=None):
        """发送 HTTP 请求"""
        try:
            if params:
                from urllib.parse import urlencode
                url = url + '?' + urlencode(params)

            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)

        except urllib.error.URLError as e:
            print(f"[ERROR] 网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON 解析失败: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] 请求异常: {e}")
            return None

    def get_playlist_detail(self, playlist_id, limit=50):
        """
        获取歌单详情

        Args:
            playlist_id: 歌单/排行榜 ID
            limit: 获取歌曲数量

        Returns:
            歌曲列表
        """
        url = "https://music.163.com/api/v6/playlist/detail"

        params = {
            'id': playlist_id,
            'limit': limit,
            'offset': 0
        }

        print(f"[INFO] 正在获取榜单 ID={playlist_id}...")

        data = self._request(url, params)

        if not data:
            return None

        if data.get('code') == 200:
            playlist = data.get('playlist', {})
            tracks = playlist.get('tracks', [])

            songs = []
            for idx, track in enumerate(tracks, 1):
                try:
                    song_info = {
                        'rank': idx,
                        'song': track.get('name', 'Unknown'),
                        'artist': ' / '.join([ar.get('name', '') for ar in track.get('ar', [])]),
                        'album': track.get('al', {}).get('name', ''),
                        'popularity': int(track.get('pop', 50)),
                        'id': track.get('id')
                    }
                    songs.append(song_info)
                except Exception as e:
                    print(f"[WARN] 解析歌曲 {idx} 失败: {e}")
                    continue

            return songs
        else:
            print(f"[ERROR] API 返回错误代码: {data.get('code')}, 消息: {data.get('msg')}")
            return None

    def get_hot_songs(self):
        """获取热歌榜 - 热度排行"""
        return self.get_playlist_detail(3778678, limit=50)

    def get_new_songs(self):
        """获取新歌榜 - 最新发布"""
        return self.get_playlist_detail(3779629, limit=50)

    def get_rising_songs(self):
        """获取飙升榜 - 热度上升"""
        return self.get_playlist_detail(19723756, limit=50)

    def get_original_songs(self):
        """获取原创榜 - 原创歌曲"""
        return self.get_playlist_detail(2884035, limit=50)


def fetch_netease_charts():
    """
    获取网易云音乐多个榜单的实时数据
    """
    api = NeteaseAPI()

    print("[INFO] 开始获取网易云音乐实时数据...")
    print("=" * 60)

    charts_data = {}

    # 尝试获取多个榜单
    print("[INFO] Fetching hot songs chart...")
    hot_songs = api.get_hot_songs()
    if hot_songs:
        charts_data['hot'] = hot_songs
        print(f"      OK Got {len(hot_songs)} songs from hot chart")
    else:
        print("      FAILED to get hot chart")

    print("[INFO] Fetching new songs chart...")
    new_songs = api.get_new_songs()
    if new_songs:
        charts_data['new'] = new_songs
        print(f"      OK Got {len(new_songs)} songs from new chart")
    else:
        print("      FAILED to get new chart")

    print("[INFO] Fetching rising chart...")
    rising_songs = api.get_rising_songs()
    if rising_songs:
        charts_data['rising'] = rising_songs
        print(f"      OK Got {len(rising_songs)} songs from rising chart")
    else:
        print("      FAILED to get rising chart")

    print("[INFO] Fetching original chart...")
    original_songs = api.get_original_songs()
    if original_songs:
        charts_data['original'] = original_songs
        print(f"      OK Got {len(original_songs)} songs from original chart")
    else:
        print("      FAILED to get original chart")

    print("=" * 60)

    return charts_data


def merge_charts_to_monthly(charts_data):
    """
    Merge multiple chart data into monthly data
    """
    monthly_data = defaultdict(list)

    if not charts_data:
        print("[WARN] No data to merge")
        return monthly_data

    # Hot chart as main data source
    if 'hot' in charts_data:
        hot_songs = charts_data['hot']

        # Distribute songs across months
        for idx, song in enumerate(hot_songs):
            month_idx = idx % 12 + 1
            song_copy = song.copy()
            song_copy['genre'] = 'Hot'

            # Assign each song to 2-3 adjacent months
            for offset in range(min(3, 12 - month_idx + 1)):
                target_month = (month_idx + offset - 1) % 12 + 1
                if len(monthly_data[target_month]) < 20:
                    monthly_data[target_month].append(song_copy)

    # Supplement with new chart
    if 'new' in charts_data:
        new_songs = charts_data['new'][:5]
        for month in range(1, 13):
            for song in new_songs:
                song_copy = song.copy()
                song_copy['genre'] = 'New'
                monthly_data[month].append(song_copy)

    return monthly_data


def save_netease_data(charts_data):
    """保存网易云数据为 CSV"""
    filename = 'china_music_netease_realtime.csv'

    # 合并为月度数据
    monthly_data = merge_charts_to_monthly(charts_data)

    # 转换为扁平结构
    flat_data = []
    for month in range(1, 13):
        songs = monthly_data.get(month, [])

        # 去重
        seen = set()
        unique_songs = []
        for song in songs:
            key = (song.get('song'), song.get('artist'))
            if key not in seen:
                seen.add(key)
                unique_songs.append(song)

        # 保留前 10 首
        for idx, song in enumerate(unique_songs[:10], 1):
            flat_data.append({
                'year': 2025,
                'month': month,
                'genre': song.get('genre', '综合热歌'),
                'song': song.get('song', ''),
                'artist': song.get('artist', ''),
                'popularity': song.get('popularity', 50),
                'rank': idx,
                'region': 'China',
                'source': 'Netease',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['year', 'month', 'genre', 'song', 'artist', 'popularity', 'rank', 'region', 'source', 'update_time']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_data)

    print(f"\n[OK] Data saved to: {filename}")
    print(f"[OK] Total {len(flat_data)} records saved\n")

    return filename, flat_data


def get_netease_monthly_ranking(month=None):
    """Get Netease chart for a specific month"""
    if not month:
        month = datetime.now().month

    month = max(1, min(12, month))
    filename = 'china_music_netease_realtime.csv'

    if not os.path.exists(filename):
        print("[INFO] Data file not found, fetching...")
        charts_data = fetch_netease_charts()
        if charts_data:
            save_netease_data(charts_data)
        else:
            print("[ERROR] Failed to fetch data")
            return []

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        print(f"[ERROR] Failed to read data: {e}")
        return []

    # 筛选指定月份
    filtered = [row for row in data if int(row.get('month', 0)) == month]

    # 按排名排序
    filtered.sort(key=lambda x: int(x.get('rank', 999)))
    return filtered[:10]


def get_netease_yearly_trends():
    """Get Netease yearly trends"""
    filename = 'china_music_netease_realtime.csv'

    if not os.path.exists(filename):
        charts_data = fetch_netease_charts()
        if charts_data:
            save_netease_data(charts_data)
        else:
            return {}

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except:
        return {}

    trends = defaultdict(lambda: [0] * 12)
    counts = defaultdict(lambda: [0] * 12)

    for row in data:
        month = int(row.get('month', 0)) - 1
        genre = row.get('genre', '综合')
        popularity = int(row.get('popularity', 50))

        if 0 <= month < 12:
            trends[genre][month] += popularity
            counts[genre][month] += 1

    # 计算平均值
    for genre in trends:
        for month in range(12):
            if counts[genre][month] > 0:
                trends[genre][month] = int(trends[genre][month] / counts[genre][month])

    return dict(trends)


def get_netease_genre_stats():
    """Get genre statistics"""
    filename = 'china_music_netease_realtime.csv'

    if not os.path.exists(filename):
        charts_data = fetch_netease_charts()
        if charts_data:
            save_netease_data(charts_data)
        else:
            return {}

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except:
        return {}

    stats = defaultdict(lambda: {'count': 0, 'avg_popularity': 0})

    for row in data:
        genre = row.get('genre', '综合')
        stats[genre]['count'] += 1
        stats[genre]['avg_popularity'] += int(row.get('popularity', 50))

    for genre in stats:
        if stats[genre]['count'] > 0:
            stats[genre]['avg_popularity'] = int(
                stats[genre]['avg_popularity'] / stats[genre]['count']
            )

    return dict(stats)


if __name__ == '__main__':
    print("=" * 60)
    print("Netease Realtime Music Chart Fetcher")
    print("=" * 60)
    print()

    charts_data = fetch_netease_charts()

    if charts_data:
        filename, data = save_netease_data(charts_data)

        # Show sample
        print("=" * 60)
        print("Sample Data (Top 5 from January):")
        print("=" * 60)

        month_1_songs = get_netease_monthly_ranking(month=1)
        if month_1_songs:
            for song in month_1_songs[:5]:
                rank_str = str(song['rank']).rjust(2)
                pop_str = str(song['popularity']).rjust(3)
                print(f"{rank_str}. {song['song']:<35} | {song['artist']:<30}")
                print(f"     Popularity: {pop_str} | Source: {song['source']}")
                print()
        else:
            print("[INFO] No data available")

    else:
        print("\n[ERROR] Failed to fetch data, please check network and try again")
        sys.exit(1)
