#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate advanced visualization charts: Water gauge and Radar chart
"""

import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.patches import Circle
import matplotlib.patches as mpatches

# Set font
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

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

def draw_water_gauge(ax, value, max_value, title, color='#1f77b4'):
    """Draw a water gauge chart"""
    # Calculate the water level (0-1)
    ratio = min(value / max_value, 1.0)

    # Draw the background circle (outer ring)
    circle_bg = Circle((0.5, 0.5), 0.45, color='lightgray', alpha=0.3, transform=ax.transAxes)
    ax.add_patch(circle_bg)

    # Draw water fill
    theta = np.linspace(0, 2*np.pi, 100)

    # Create wave effect
    amplitude = 0.02
    frequency = 3
    wave = amplitude * np.sin(frequency * theta)

    # Calculate the water level height
    water_height = 0.5 - 0.45 * (1 - ratio) + wave

    # Create water polygon
    water_theta = np.linspace(0, np.pi, 100)
    water_x = 0.5 + 0.45 * np.cos(water_theta)
    water_y = 0.5 - 0.45 * np.sin(water_theta)

    # Add wave to water
    wave_simple = 0.02 * np.sin(3 * water_theta)

    # Fill water
    water_y_fill = 0.5 - 0.45 * (1 - ratio)
    ax.fill_between([0, 1], [water_y_fill]*2, [0, 0],
                     alpha=0.6, color=color, transform=ax.transAxes)

    # Add wave pattern
    for i in range(3):
        phase = i * 2 * np.pi / 3
        wave_x = np.linspace(0, 1, 100)
        wave_y = water_y_fill + 0.03 * np.sin(6 * np.pi * wave_x + phase)
        ax.plot(wave_x, wave_y, color=color, alpha=0.5, linewidth=1.5, transform=ax.transAxes)

    # Draw the outer circle
    circle_outer = Circle((0.5, 0.5), 0.45, fill=False, edgecolor='darkgray',
                         linewidth=3, transform=ax.transAxes)
    ax.add_patch(circle_outer)

    # Add percentage text
    percentage = int(ratio * 100)
    ax.text(0.5, 0.5, '{}%'.format(percentage),
           transform=ax.transAxes, fontsize=40, fontweight='bold',
           ha='center', va='center', color='darkblue')

    # Add title
    ax.text(0.5, 0.05, title,
           transform=ax.transAxes, fontsize=14, fontweight='bold',
           ha='center', va='bottom')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

def chart_9_water_gauge(data):
    """Chart 9: Water gauge for genre popularity"""
    # Calculate statistics for each genre
    genre_stats = defaultdict(lambda: {'popularity': 0, 'count': 0})

    for item in data:
        genre_stats[item['genre']]['popularity'] += item['popularity']
        genre_stats[item['genre']]['count'] += 1

    # Get top 4 genres
    genres_sorted = sorted(
        [(genre, stats['popularity'] / stats['count'])
         for genre, stats in genre_stats.items()],
        key=lambda x: x[1],
        reverse=True
    )[:4]

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Genre Popularity Water Gauge', fontsize=18, fontweight='bold', y=0.98)

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']

    for idx, (genre, popularity) in enumerate(genres_sorted):
        ax = fig.add_subplot(2, 2, idx + 1)
        max_pop = 100
        draw_water_gauge(ax, popularity, max_pop, genre.upper(), colors[idx])

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('{}/09_water_gauge.png'.format(OUTPUT_DIR), dpi=300, bbox_inches='tight')
    plt.close()
    print("[9/10] Water gauge chart generated")

def chart_10_radar_chart(data):
    """Chart 10: Radar chart for genre characteristics"""
    # Calculate statistics for each genre
    genre_stats = defaultdict(lambda: {
        'count': 0,
        'avg_popularity': 0,
        'max_rank': 0,
        'song_count': 0,
        'artist_count': set()
    })

    for item in data:
        genre = item['genre']
        genre_stats[genre]['count'] += 1
        genre_stats[genre]['avg_popularity'] += item['popularity']
        genre_stats[genre]['max_rank'] = max(genre_stats[genre]['max_rank'], item['rank'])
        genre_stats[genre]['song_count'] += 1
        genre_stats[genre]['artist_count'].add(item['artist'])

    # Calculate metrics
    metrics = {}
    for genre, stats in genre_stats.items():
        metrics[genre] = {
            'Popularity': stats['avg_popularity'] / max(stats['count'], 1),
            'Song Count': min(stats['song_count'] / 50, 100),  # Normalize to 0-100
            'Artist Count': min(len(stats['artist_count']), 100),  # Cap at 100
            'Consistency': (100 - (stats['max_rank'] / 13 * 100)),  # Lower rank = higher score
            'Influence': (stats['count'] / 50) * 100  # Normalize influence
        }

    # Get top 5 genres
    top_genres = sorted(metrics.keys(),
                       key=lambda x: metrics[x]['Popularity'],
                       reverse=True)[:5]

    # Prepare data for radar chart
    categories = ['Popularity', 'Song Count', 'Artist Count', 'Consistency', 'Influence']
    num_vars = len(categories)

    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    fig, axes = plt.subplots(2, 3, figsize=(18, 12), subplot_kw=dict(projection='polar'))
    fig.suptitle('Genre Characteristics Radar Chart', fontsize=18, fontweight='bold', y=0.98)

    axes = axes.flatten()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#95E1D3']

    for idx, (ax, genre) in enumerate(zip(axes, top_genres + [''])):
        if genre:
            values = [
                metrics[genre]['Popularity'],
                metrics[genre]['Song Count'],
                metrics[genre]['Artist Count'],
                metrics[genre]['Consistency'],
                metrics[genre]['Influence']
            ]
            values += values[:1]  # Complete the circle

            ax.plot(angles, values, 'o-', linewidth=2, color=colors[idx], label=genre.upper())
            ax.fill(angles, values, alpha=0.25, color=colors[idx])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, size=10)
            ax.set_ylim(0, 100)
            ax.set_title(genre.upper(), fontsize=14, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
        else:
            # Hide the last subplot
            ax.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('{}/10_radar_chart.png'.format(OUTPUT_DIR), dpi=300, bbox_inches='tight')
    plt.close()
    print("[10/10] Radar chart generated")

def main():
    """Main function"""
    print("\nGenerating advanced visualization charts...")
    print("=" * 50)

    # Load data
    data = load_data()
    print("Loaded {} data records\n".format(len(data)))

    # Generate charts
    chart_9_water_gauge(data)
    chart_10_radar_chart(data)

    print("=" * 50)
    print("Advanced charts generated to: {}".format(OUTPUT_DIR))
    print("\nNew charts:")
    print("  9. 09_water_gauge.png - Genre popularity water gauge")
    print("  10. 10_radar_chart.png - Genre characteristics radar chart")
    print("\nAll 10 charts ready for PowerPoint!")

if __name__ == '__main__':
    main()
