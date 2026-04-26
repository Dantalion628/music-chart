"""
Netease Cloud Music Real-time Chart Data
Fetch data from official Netease API and map to virtual months
- Month 1: Hot Chart (热歌榜)
- Month 2: New Songs (新歌榜)
- Month 3: Rising (飙升榜)
- Month 4: Original (原创榜)
- Month 5-12: Cycle back or empty
"""

import json
import csv
import os
import urllib.request
import urllib.error
from datetime import datetime
from collections import defaultdict
import sys
import re

def detect_genre(song_name, artist_name):
    """
    Detect genre based on song name and artist name
    Uses keyword matching and common patterns
    """

    # Combine text for analysis
    text = (song_name + ' ' + artist_name).lower()

    # Genre keywords mapping
    genre_keywords = {
        'pop': ['pop', '流行', '说好不', '说好了', '光年', '光辉', '星辰', '说好', '告白', '一生', '春风', '好久', '告白气球', '漂洋过海'],
        'rock': ['rock', '摇滚', '黑梦', '烟火', '光年之外', '曾经', '晴天', '蜀国', '黑龙', '许巍', '梦想', '山河'],
        'hiphop': ['hip-hop', '说唱', 'rap', '火', 'freestyle', 'gai', '中国说唱', 'vava', 'young', 'mc天佑', '打工人', '嘻哈'],
        'electronic': ['electronic', '电子', '电音', 'edm', 'dj', 'house', 'synth', '往后余生', '潮鸣', '未来', '星河', '冲破'],
        'folk': ['民谣', '民族', '成都', '赵雷', '理想', '南山南', '烟火', '梦里花', '故乡'],
        'rnb': ['r&b', 'rnb', '节奏蓝调', '韵律'],
        'indie': ['独立', 'indie', '独立音乐'],
        'jazz': ['jazz', '爵士'],
        'classical': ['古典', '交响', 'classical'],
    }

    # Check keywords
    for genre, keywords in genre_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return genre

    # Default genre based on some heuristics
    if '梦' in text or '风' in text or '光' in text:
        return 'pop'
    elif 'dj' in text or 'edm' in text:
        return 'electronic'
    elif '摇' in text or '滚' in text:
        return 'rock'
    elif '说唱' in text or 'rap' in text:
        return 'hiphop'

    # Default to pop
    return 'pop'


class NeteaseAPI:
    """Netease Cloud Music API Client"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://music.163.com',
        }

    def _request(self, url, params=None):
        """Send HTTP request"""
        try:
            if params:
                from urllib.parse import urlencode
                url = url + '?' + urlencode(params)

            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)

        except urllib.error.URLError as e:
            print(f"[ERROR] Network request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode failed: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            return None

    def get_playlist_detail(self, playlist_id, limit=50):
        """
        Get playlist details

        Args:
            playlist_id: Playlist/Chart ID
            limit: Number of songs to fetch

        Returns:
            List of songs
        """
        url = "https://music.163.com/api/v6/playlist/detail"

        params = {
            'id': playlist_id,
            'limit': limit,
            'offset': 0
        }

        print(f"[INFO] Fetching chart ID={playlist_id}...")

        data = self._request(url, params)

        if not data:
            return None

        if data.get('code') == 200:
            playlist = data.get('playlist', {})
            tracks = playlist.get('tracks', [])

            songs = []
            for idx, track in enumerate(tracks, 1):
                try:
                    name = track.get('name', 'Unknown')
                    artist = ' / '.join([ar.get('name', '') for ar in track.get('ar', [])])

                    song_info = {
                        'rank': idx,
                        'name': name,
                        'artist': artist,
                        'album': track.get('al', {}).get('name', ''),
                        'popularity': int(track.get('pop', 50)),
                        'id': track.get('id'),
                        'duration': track.get('dt', 0) // 1000,
                        'genre': detect_genre(name, artist)
                    }
                    songs.append(song_info)
                except Exception as e:
                    print(f"[WARN] Failed to parse song {idx}: {e}")
                    continue

            return songs
        else:
            print(f"[ERROR] API returned error code: {data.get('code')}, message: {data.get('msg')}")
            return None

    def get_hot_songs(self):
        """Get hot chart - 热歌榜"""
        return self.get_playlist_detail(3778678, limit=30)

    def get_new_songs(self):
        """Get new songs chart - 新歌榜"""
        return self.get_playlist_detail(3779629, limit=30)

    def get_rising_songs(self):
        """Get rising chart - 飙升榜"""
        return self.get_playlist_detail(19723756, limit=30)

    def get_original_songs(self):
        """Get original chart - 原创榜"""
        return self.get_playlist_detail(2884035, limit=30)


def fetch_netease_charts():
    """
    Fetch all four Netease charts
    """
    api = NeteaseAPI()

    print("[INFO] Fetching Netease real-time chart data...")
    print("=" * 60)

    charts_data = {}

    print("[INFO] Fetching hot chart...")
    hot_songs = api.get_hot_songs()
    if hot_songs:
        charts_data['hot'] = hot_songs
        print(f"      OK Got {len(hot_songs)} songs")
    else:
        print("      FAILED")

    print("[INFO] Fetching new songs chart...")
    new_songs = api.get_new_songs()
    if new_songs:
        charts_data['new'] = new_songs
        print(f"      OK Got {len(new_songs)} songs")
    else:
        print("      FAILED")

    print("[INFO] Fetching rising chart...")
    rising_songs = api.get_rising_songs()
    if rising_songs:
        charts_data['rising'] = rising_songs
        print(f"      OK Got {len(rising_songs)} songs")
    else:
        print("      FAILED")

    print("[INFO] Fetching original chart...")
    original_songs = api.get_original_songs()
    if original_songs:
        charts_data['original'] = original_songs
        print(f"      OK Got {len(original_songs)} songs")
    else:
        print("      FAILED")

    print("=" * 60)

    return charts_data


def save_netease_data(charts_data):
    """Save Netease data to CSV"""
    filename = 'china_music_netease_realtime.csv'

    # Map charts to virtual months
    # Month 1: Hot, Month 2: New, Month 3: Rising, Month 4: Original
    chart_month_mapping = {
        'hot': (1, 'Hot Chart'),
        'new': (2, 'New Songs'),
        'rising': (3, 'Rising'),
        'original': (4, 'Original')
    }

    flat_data = []

    for chart_key, (month, chart_name) in chart_month_mapping.items():
        if chart_key in charts_data:
            songs = charts_data[chart_key]

            for song in songs[:10]:  # Keep top 10 from each chart
                flat_data.append({
                    'year': 2025,
                    'month': month,
                    'chart_type': chart_name,
                    'song_genre': song.get('genre', 'pop'),
                    'song': song.get('name', ''),
                    'artist': song.get('artist', ''),
                    'popularity': song.get('popularity', 50),
                    'rank': song.get('rank', 0),
                    'region': 'China',
                    'source': 'Netease',
                    'song_id': song.get('id', 0),
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['year', 'month', 'chart_type', 'song_genre', 'song', 'artist', 'popularity', 'rank', 'region', 'source', 'song_id', 'update_time']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_data)

    print(f"\n[OK] Data saved to: {filename}")
    print(f"[OK] Total {len(flat_data)} records\n")

    return filename, flat_data


def get_netease_monthly_ranking(month=None):
    """Get Netease chart for a specific month (virtual)"""
    if not month:
        month = datetime.now().month

    month = max(1, min(4, month))  # Only support months 1-4
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

    # Filter by month
    filtered = [row for row in data if int(row.get('month', 0)) == month]

    # Sort by rank
    filtered.sort(key=lambda x: int(x.get('rank', 999)))
    return filtered[:10]


def get_netease_yearly_trends():
    """Get Netease trends for 4 chart types"""
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

    trends = defaultdict(lambda: [0, 0, 0, 0])  # Only 4 chart types
    counts = defaultdict(lambda: [0, 0, 0, 0])

    for row in data:
        month = int(row.get('month', 0)) - 1  # 0-3 index
        genre = row.get('genre', 'Mixed')
        popularity = int(row.get('popularity', 50))

        if 0 <= month < 4:
            trends[genre][month] += popularity
            counts[genre][month] += 1

    # Calculate average
    for genre in trends:
        for month in range(4):
            if counts[genre][month] > 0:
                trends[genre][month] = int(trends[genre][month] / counts[genre][month])
            else:
                trends[genre][month] = 0

    return dict(trends)


def get_netease_genre_stats():
    """Get genre statistics for each chart type"""
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

    # Map month to chart type
    month_to_chart = {
        '1': 'hot',
        '2': 'new',
        '3': 'rising',
        '4': 'original'
    }

    # Structure: {chart_type: {genre: count}}
    stats = defaultdict(lambda: defaultdict(int))

    for row in data:
        month = row.get('month', '1')
        chart_type = month_to_chart.get(month, 'hot')
        genre = row.get('song_genre', 'pop')

        stats[chart_type][genre] += 1

    # Convert to simple dict
    result = {}
    for chart_type in stats:
        result[chart_type] = dict(stats[chart_type])

    return result


if __name__ == '__main__':
    print("=" * 60)
    print("Netease Real-time Music Chart Fetcher")
    print("=" * 60)
    print()

    charts_data = fetch_netease_charts()

    if charts_data:
        filename, data = save_netease_data(charts_data)

        # Show samples
        print("=" * 60)
        print("Available Charts:")
        print("=" * 60)
        print("Month 1: Hot Chart (热歌榜)")
        print("Month 2: New Songs (新歌榜)")
        print("Month 3: Rising (飙升榜)")
        print("Month 4: Original (原创榜)")
        print()

        for month in range(1, 5):
            month_songs = get_netease_monthly_ranking(month=month)
            if month_songs:
                chart_names = {1: 'Hot', 2: 'New', 3: 'Rising', 4: 'Original'}
                print(f"\n{chart_names.get(month, 'Unknown')} Chart (Month {month}) - Top 5:")
                print("-" * 60)
                for song in month_songs[:5]:
                    print(f"{song['rank']:2d}. {song['song']:<40} | {song['artist']:<25}")

    else:
        print("\n[ERROR] Failed to fetch data, check network and try again")
        sys.exit(1)
