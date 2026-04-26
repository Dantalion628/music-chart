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
                    song_info = {
                        'rank': idx,
                        'name': track.get('name', 'Unknown'),
                        'artist': ' / '.join([ar.get('name', '') for ar in track.get('ar', [])]),
                        'album': track.get('al', {}).get('name', ''),
                        'popularity': int(track.get('pop', 50)),
                        'id': track.get('id'),
                        'duration': track.get('dt', 0) // 1000
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

    for chart_key, (month, genre_name) in chart_month_mapping.items():
        if chart_key in charts_data:
            songs = charts_data[chart_key]

            for song in songs[:10]:  # Keep top 10 from each chart
                flat_data.append({
                    'year': 2025,
                    'month': month,
                    'genre': genre_name,
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
        fieldnames = ['year', 'month', 'genre', 'song', 'artist', 'popularity', 'rank', 'region', 'source', 'song_id', 'update_time']
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
        genre = row.get('genre', 'Mixed')
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
