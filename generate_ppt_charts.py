#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate analytical charts for PPT presentation
Generate 8 high-quality data visualization charts
"""

import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# Set font
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
plt.style.use('default')

# Create output directory
OUTPUT_DIR = 'ppt_charts'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_data():
    """Load CSV data"""
    data = []
    with open('processed_data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'year': int(row['year']),
                'rank': int(row['rank']),
                'song': row['song'],
                'artist': row['artist'],
                'genre': row['genre'].strip(),
                'popularity': int(row['popularity'])
            })
    return data

def chart_1_genre_distribution(data):
    """Chart 1: Genre distribution pie chart"""
    genre_counts = defaultdict(int)
    for item in data:
        genre_counts[item['genre']] += 1

    genres = list(genre_counts.keys())
    counts = list(genre_counts.values())

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.Set3(np.linspace(0, 1, len(genres)))

    wedges, texts, autotexts = ax.pie(
        counts,
        labels=genres,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 12}
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_weight('bold')

    ax.set_title('Music Genre Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/01_genre_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[1/8] Genre distribution pie chart generated")

def chart_2_yearly_trends(data):
    """Chart 2: Yearly trend line chart"""
    yearly_count = defaultdict(int)
    yearly_popularity = defaultdict(int)

    for item in data:
        yearly_count[item['year']] += 1
        yearly_popularity[item['year']] += item['popularity']

    years = sorted(yearly_count.keys())
    counts = [yearly_count[year] for year in years]
    avg_popularity = [yearly_popularity[year] // yearly_count[year] for year in years]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Song count trend
    ax1.plot(years, counts, marker='o', linewidth=2.5, markersize=8, color='#2E86AB')
    ax1.fill_between(years, counts, alpha=0.3, color='#2E86AB')
    ax1.set_title('Annual Song Count Trend', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Songs', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(min(years)-0.5, max(years)+0.5)

    # Popularity trend
    ax2.plot(years, avg_popularity, marker='s', linewidth=2.5, markersize=8, color='#A23B72')
    ax2.fill_between(years, avg_popularity, alpha=0.3, color='#A23B72')
    ax2.set_title('Annual Average Popularity Trend', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Average Popularity', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(min(years)-0.5, max(years)+0.5)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/02_yearly_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[2/8] Yearly trends line chart generated")

def chart_3_top_genres(data):
    """Chart 3: Top genres bar chart"""
    genre_popularity = defaultdict(list)

    for item in data:
        genre_popularity[item['genre']].append(item['popularity'])

    genres = sorted(genre_popularity.keys())
    avg_popularity = [sum(genre_popularity[g]) / len(genre_popularity[g]) for g in genres]

    # Sort by popularity
    sorted_pairs = sorted(zip(genres, avg_popularity), key=lambda x: x[1], reverse=True)
    genres, avg_popularity = zip(*sorted_pairs)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.viridis(np.linspace(0, 1, len(genres)))

    bars = ax.barh(genres, avg_popularity, color=colors)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, avg_popularity)):
        ax.text(val + 0.5, i, '{:.1f}'.format(val), va='center', fontsize=11, fontweight='bold')

    ax.set_xlabel('Average Popularity', fontsize=12, fontweight='bold')
    ax.set_title('Genre Popularity Rankings', fontsize=16, fontweight='bold', pad=20)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/03_top_genres.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[3/8] Top genres bar chart generated")

def chart_4_genre_trends(data):
    """Chart 4: Genre trends over time"""
    genre_by_year = defaultdict(lambda: defaultdict(int))

    for item in data:
        genre_by_year[item['genre']][item['year']] += 1

    fig, ax = plt.subplots(figsize=(14, 8))

    years = sorted(set(item['year'] for item in data))

    for genre in ['pop', 'rock', 'hip-hop', 'r&b', 'electronic']:
        if genre in genre_by_year:
            counts = [genre_by_year[genre].get(year, 0) for year in years]
            ax.plot(years, counts, marker='o', linewidth=2.5, markersize=8, label=genre.upper())

    ax.set_title('Genre Trends Over Time', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Songs', fontsize=12, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(years)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/04_genre_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[4/8] Genre trends chart generated")

def chart_5_popularity_distribution(data):
    """Chart 5: Popularity distribution histogram"""
    popularity_scores = [item['popularity'] for item in data]

    fig, ax = plt.subplots(figsize=(12, 8))

    n, bins, patches = ax.hist(popularity_scores, bins=20, color='#FF6B6B', alpha=0.7, edgecolor='black')

    # Add gradient coloring
    cm = plt.cm.RdYlGn
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    col = bin_centers - min(bin_centers)
    col /= max(col)

    for c, p in zip(col, patches):
        plt.setp(p, 'facecolor', cm(c))

    ax.set_title('Popularity Distribution', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Popularity Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Songs', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Add statistics
    stats_text = 'Mean: {:.1f}\nMedian: {:.1f}\nStd Dev: {:.1f}'.format(
        np.mean(popularity_scores), np.median(popularity_scores), np.std(popularity_scores)
    )
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/05_popularity_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[5/8] Popularity distribution histogram generated")

def chart_6_top_10_artists(data):
    """Chart 6: Top 10 artists"""
    artist_count = defaultdict(int)
    artist_avg_popularity = defaultdict(list)

    for item in data:
        artist_count[item['artist']] += 1
        artist_avg_popularity[item['artist']].append(item['popularity'])

    # Calculate average popularity and sort
    artists_sorted = sorted(
        [(artist, count, sum(artist_avg_popularity[artist]) / len(artist_avg_popularity[artist]))
         for artist, count in artist_count.items()],
        key=lambda x: x[2],
        reverse=True
    )[:10]

    artists = [a[0] for a in artists_sorted]
    avg_pops = [a[2] for a in artists_sorted]

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.plasma(np.linspace(0, 1, len(artists)))

    bars = ax.bar(range(len(artists)), avg_pops, color=colors)
    ax.set_xticks(range(len(artists)))
    ax.set_xticklabels(artists, rotation=45, ha='right', fontsize=11)

    # Add value labels
    for bar, val in zip(bars, avg_pops):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                '{:.1f}'.format(val), ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('Average Popularity', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Artists (by Average Popularity)', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/06_top_10_artists.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[6/8] Top 10 artists chart generated")

def chart_7_genre_popularity_heatmap(data):
    """Chart 7: Genre and popularity heatmap"""
    # Prepare data
    years = sorted(set(item['year'] for item in data))
    genres = sorted(set(item['genre'] for item in data))

    heatmap_data = np.zeros((len(genres), len(years)))

    for i, genre in enumerate(genres):
        for j, year in enumerate(years):
            genre_year_items = [item for item in data if item['genre'] == genre and item['year'] == year]
            if genre_year_items:
                heatmap_data[i, j] = sum(item['popularity'] for item in genre_year_items) / len(genre_year_items)

    fig, ax = plt.subplots(figsize=(14, 8))

    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')

    ax.set_xticks(range(len(years)))
    ax.set_yticks(range(len(genres)))
    ax.set_xticklabels(years, rotation=45)
    ax.set_yticklabels(genres)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Average Popularity', rotation=270, labelpad=20, fontsize=11)

    ax.set_title('Genre and Year Popularity Heatmap', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Genre', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/07_genre_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[7/8] Genre popularity heatmap generated")

def chart_8_decade_summary(data):
    """Chart 8: Decade summary comparison"""
    decade_data = defaultdict(lambda: {'genres': defaultdict(int), 'popularity': 0, 'count': 0})

    for item in data:
        decade = (item['year'] // 10) * 10
        decade_key = '{0}s'.format(decade)
        decade_data[decade_key]['genres'][item['genre']] += 1
        decade_data[decade_key]['popularity'] += item['popularity']
        decade_data[decade_key]['count'] += 1

    decades = sorted(decade_data.keys())
    avg_popularity = [decade_data[d]['popularity'] / decade_data[d]['count'] for d in decades]
    song_counts = [decade_data[d]['count'] for d in decades]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Left: Song count by decade
    colors1 = plt.cm.Blues(np.linspace(0.4, 0.9, len(decades)))
    bars1 = ax1.bar(decades, song_counts, color=colors1, edgecolor='black', linewidth=1.5)

    for bar, count in zip(bars1, song_counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                '{}'.format(int(count)), ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax1.set_ylabel('Number of Songs', fontsize=12, fontweight='bold')
    ax1.set_title('Song Count by Decade', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    # Right: Average popularity by decade
    colors2 = plt.cm.Reds(np.linspace(0.4, 0.9, len(decades)))
    bars2 = ax2.bar(decades, avg_popularity, color=colors2, edgecolor='black', linewidth=1.5)

    for bar, pop in zip(bars2, avg_popularity):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                '{:.1f}'.format(pop), ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax2.set_ylabel('Average Popularity', fontsize=12, fontweight='bold')
    ax2.set_title('Average Popularity by Decade', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.suptitle('Decade Summary Analysis', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/08_decade_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[8/8] Decade summary chart generated")

def main():
    """Main function"""
    print("\nGenerating data analysis charts...")
    print("=" * 50)

    # Load data
    data = load_data()
    print("Loaded {} data records\n".format(len(data)))

    # Generate charts
    chart_1_genre_distribution(data)
    chart_2_yearly_trends(data)
    chart_3_top_genres(data)
    chart_4_genre_trends(data)
    chart_5_popularity_distribution(data)
    chart_6_top_10_artists(data)
    chart_7_genre_popularity_heatmap(data)
    chart_8_decade_summary(data)

    print("=" * 50)
    print("All charts generated to: {}".format(OUTPUT_DIR))
    print("\nGenerated chart list:")
    print("  1. 01_genre_distribution.png - Genre distribution pie chart")
    print("  2. 02_yearly_trends.png - Annual trends line chart")
    print("  3. 03_top_genres.png - Genre popularity rankings")
    print("  4. 04_genre_trends.png - Genre trends over time")
    print("  5. 05_popularity_distribution.png - Popularity distribution histogram")
    print("  6. 06_top_10_artists.png - Top 10 artists by popularity")
    print("  7. 07_genre_heatmap.png - Genre and year heatmap")
    print("  8. 08_decade_summary.png - Decade summary comparison")
    print("\nReady to add to PowerPoint!")

if __name__ == '__main__':
    main()
