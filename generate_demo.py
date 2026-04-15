"""
直接生成示例数据（不需要下载）
用于快速测试和演示
"""

import csv
from collections import defaultdict

def generate_demo_data():
    """生成演示数据"""
    songs_by_period = {
        (1995, 1997): [
            ('Waterfalls', 'TLC', 'r&b', 95),
            ('Creep', 'Radiohead', 'rock', 92),
            ('No Scrubs', 'TLC', 'r&b', 93),
            ('Bitter Sweet Symphony', 'The Verve', 'rock', 89),
            ('Wonderwall', 'Oasis', 'rock', 91),
            ('One Sweet Day', 'Mariah Carey', 'pop', 88),
            ('Exhale (Shoop)', 'Whitney Houston', 'r&b', 87),
            ('I Will Make Love to You', 'Boyz II Men', 'r&b', 86),
            ('Vision of Love', 'Mariah Carey', 'pop', 85),
            ('All For Love', 'Rod Stewart', 'pop', 84),
        ],
        (1998, 2001): [
            ('Believe', 'Cher', 'pop', 94),
            ('...Baby One More Time', 'Britney Spears', 'pop', 96),
            ('Bye Bye Bye', 'N*SYNC', 'pop', 95),
            ('Crazy in Love', 'Beyoncé', 'r&b', 93),
            ('Hips Don\'t Lie', 'Shakira', 'pop', 92),
            ('I\'ll Be Missing You', 'Puff Daddy', 'hip-hop', 91),
            ('Lady Marmalade', 'Christina Aguilera', 'pop', 90),
            ('Beautiful', 'Christina Aguilera', 'pop', 89),
            ('Toxic', 'Britney Spears', 'pop', 88),
            ('Yeah!', 'Usher', 'r&b', 87),
        ],
        (2002, 2005): [
            ('Without Me', 'Eminem', 'hip-hop', 97),
            ('In Da Club', '50 Cent', 'hip-hop', 96),
            ('Hot in Herre', 'Nelly', 'hip-hop', 95),
            ('Hollaback Girl', 'Gwen Stefani', 'pop', 93),
            ('SexyBack', 'Justin Timberlake', 'pop', 92),
            ('Lose Yourself', 'Eminem', 'hip-hop', 94),
            ('Gold Digger', 'Kanye West', 'hip-hop', 93),
            ('Single Ladies', 'Beyoncé', 'pop', 91),
            ('Since U Been Gone', 'Kelly Clarkson', 'pop', 90),
            ('Beautiful', 'Christina Aguilera', 'pop', 89),
        ],
        (2006, 2009): [
            ('Umbrella', 'Rihanna', 'pop', 95),
            ('Single Ladies', 'Beyoncé', 'pop', 96),
            ('Poker Face', 'Lady Gaga', 'pop', 94),
            ('I Gotta Feeling', 'Black Eyed Peas', 'pop', 93),
            ('Bad Romance', 'Lady Gaga', 'pop', 92),
            ('Viva la Vida', 'Coldplay', 'rock', 90),
            ('Use Somebody', 'Kings of Leon', 'rock', 88),
            ('Sex on Fire', 'Kings of Leon', 'rock', 87),
            ('Bleeding Love', 'Leona Lewis', 'pop', 89),
            ('Chasing Pavements', 'Adele', 'pop', 88),
        ],
        (2010, 2015): [
            ('Rolling in the Deep', 'Adele', 'pop', 98),
            ('Hotline Bling', 'Drake', 'hip-hop', 97),
            ('Shake It Off', 'Taylor Swift', 'pop', 96),
            ('Uptown Funk', 'Mark Ronson', 'pop', 95),
            ('Lean On', 'Major Lazer', 'electronic', 94),
            ('Wake Me Up', 'Avicii', 'electronic', 93),
            ('Titanium', 'David Guetta', 'electronic', 92),
            ('Levels', 'Avicii', 'electronic', 91),
            ('Animals', 'Martin Garrix', 'electronic', 90),
            ('Clarity', 'Zedd', 'electronic', 89),
        ],
        (2016, 2020): [
            ('One Dance', 'Drake', 'hip-hop', 99),
            ('Blinding Lights', 'The Weeknd', 'pop', 98),
            ('Bad Guy', 'Billie Eilish', 'pop', 97),
            ('HUMBLE.', 'Kendrick Lamar', 'hip-hop', 96),
            ('God\'s Plan', 'Drake', 'hip-hop', 95),
            ('Shut Up and Dance', 'WALK THE MOON', 'pop', 94),
            ('Closer', 'The Chainsmokers', 'electronic', 93),
            ('This Is What You Came For', 'Calvin Harris', 'electronic', 92),
            ('Starboy', 'The Weeknd', 'pop', 91),
            ('Shape of You', 'Ed Sheeran', 'pop', 90),
        ]
    }

    data = []
    years = list(range(1995, 2021))

    for year in years:
        # 找到对应时期的歌曲
        songs = None
        for year_range, songs_list in songs_by_period.items():
            if year_range[0] <= year <= year_range[1]:
                songs = songs_list
                break

        if not songs:
            songs = [('Sample Song', 'Sample Artist', 'pop', 50)]

        # 为每年生成50条记录（10个流派 × 5条）
        genre_counts = defaultdict(int)
        for i in range(50):
            song, artist, genre, base_popularity = songs[i % len(songs)]

            # 添加一些随机变化
            popularity = max(20, min(100, base_popularity + (i % 20 - 10)))

            data.append({
                'year': year,
                'date': f'{year}-{(i % 52) // 4 + 1:02d}-01',
                'rank': (i % 100) + 1,
                'song': f'{song}',
                'artist': artist,
                'genre': genre,
                'popularity': popularity
            })

            genre_counts[genre] += 1

    return data

def main():
    print("[INFO] Generating demo data...")
    data = generate_demo_data()

    # 保存为CSV
    filename = 'processed_data.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['year', 'date', 'rank', 'song', 'artist', 'genre', 'popularity'])
        writer.writeheader()
        writer.writerows(data)

    print("[OK] Demo data generated: " + filename)
    print("[OK] Total records: " + str(len(data)))

    # 统计
    from collections import Counter
    years = [d['year'] for d in data]
    genres = [d['genre'] for d in data]

    print("\nStatistics:")
    print("  Time range: {}-{}".format(min(years), max(years)))
    print("  Total genres: {}".format(len(set(genres))))
    print("  Genre distribution: {}".format(dict(Counter(genres))))

if __name__ == '__main__':
    main()
