// 应用状态
let currentYear = 1995;
let currentMonth = new Date().getMonth() + 1;
let currentPlaylist = [];
let currentTrackIndex = 0;
let isPlaying = false;
let spotifyAccessToken = null;
let currentChartType = 'line';
let currentChinaChartType = 'line';

// 图表实例（初始为null）
let trendsChartInstance = null;
let chinaTrendsChartInstance = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupYearSelector();
    setupChartTypeSelector();
    setupChinaNavigation();
    setupMonthSelector();

    loadPeriods();
    loadTrends('line');
    loadRankings(1995);
    loadChinaTrends('line');
    loadChinaRankings('hot');
    loadChinaStats();
});

// ═══════════════════════════════════════════════════
// 基础导航和UI控制
// ═══════════════════════════════════════════════════

function setupNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', switchTab);
    });
}

function setupChinaNavigation() {
    document.querySelectorAll('.china-tab-btn').forEach(btn => {
        btn.addEventListener('click', switchChinaTab);
    });
}

function switchTab(e) {
    const tabName = e.target.dataset.tab;

    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');

    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');

    if (tabName === 'trends') {
        setTimeout(() => {
            if (trendsChartInstance && typeof trendsChartInstance.resize === 'function') {
                trendsChartInstance.resize();
            }
        }, 100);
    } else if (tabName === 'china') {
        setTimeout(() => {
            if (chinaTrendsChartInstance && typeof chinaTrendsChartInstance.resize === 'function') {
                chinaTrendsChartInstance.resize();
            }
        }, 100);
    }
}

function switchChinaTab(e) {
    const tabName = 'china-' + e.target.dataset.chinaTab;

    document.querySelectorAll('.china-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');

    document.querySelectorAll('.china-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');

    if (e.target.dataset.chinaTab === 'trends') {
        setTimeout(() => {
            if (chinaTrendsChartInstance && typeof chinaTrendsChartInstance.resize === 'function') {
                chinaTrendsChartInstance.resize();
            }
        }, 100);
    }
}

// 图表类型选择器
function setupChartTypeSelector() {
    document.querySelectorAll('.chart-type-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.chart-type-btn').forEach(b => {
                b.classList.remove('active');
            });
            e.target.classList.add('active');
            currentChartType = e.target.dataset.chart;
            loadTrends(currentChartType);
        });
    });

    // 中国音乐图表选择
    document.querySelectorAll('.china-chart-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.china-chart-btn').forEach(b => {
                b.classList.remove('active');
            });
            e.target.classList.add('active');
            currentChinaChartType = e.target.dataset.chart;
            loadChinaTrends(currentChinaChartType);
        });
    });
}

function setupYearSelector() {
    document.querySelectorAll('.year-btn').forEach(btn => {
        btn.addEventListener('click', selectYear);
    });
}

function setupMonthSelector() {
    // Changed to chart selector for Netease charts
    document.querySelectorAll('.china-ranking-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.china-ranking-btn').forEach(b => {
                b.classList.remove('active');
            });
            e.target.classList.add('active');
            const chartType = e.target.dataset.chart;
            loadChinaRankings(chartType);
        });
    });
}

function selectYear(e) {
    const year = parseInt(e.target.dataset.year);
    currentYear = year;

    document.querySelectorAll('.year-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');

    loadRankings(year);
}

// ═══════════════════════════════════════════════════
// 国际音乐数据加载
// ═══════════════════════════════════════════════════

async function loadPeriods() {
    try {
        const response = await fetch('/api/periods');
        const data = await response.json();

        const grid = document.getElementById('periodsGrid');
        grid.innerHTML = '';

        const years = [1995, 2000, 2005, 2010, 2015, 2020];
        years.forEach(year => {
            const key = `period_${year}`;
            if (data[key]) {
                const period = data[key];
                const card = createPeriodCard(period);
                grid.appendChild(card);
            }
        });
    } catch (error) {
        console.error('加载周期数据失败:', error);
    }
}

function createPeriodCard(period) {
    const card = document.createElement('div');
    card.className = 'period-card';

    let genresHtml = '<div class="genre-list">';
    period.genres.forEach((genre, index) => {
        genresHtml += `
            <div class="genre-item">
                <span class="genre-name">${index + 1}. ${genre.name}</span>
                <span class="genre-count">${genre.count}首</span>
            </div>
        `;
    });

    genresHtml += '</div>';

    if (period.genres[0] && period.genres[0].sample_songs) {
        genresHtml += '<div class="sample-songs"><strong>代表歌曲：</strong>';
        period.genres[0].sample_songs.forEach(song => {
            const neteaseUrl = `https://music.163.com/search/get?s=${encodeURIComponent(song.song + ' ' + song.artist)}&type=1`;
            genresHtml += `
                <div class="sample-song" onclick="window.open('${neteaseUrl}', '_blank')" style="cursor: pointer;" title="在网易云打开">
                    <div class="sample-song-title">🎵 ${song.song}</div>
                    <div class="sample-song-artist">${song.artist}</div>
                </div>
            `;
        });
        genresHtml += '</div>';
    }

    card.innerHTML = `
        <div class="period-year">${period.year}</div>
        <div class="period-range">${period.period}年</div>
        ${genresHtml}
    `;

    return card;
}

async function loadTrends(chartType = 'line') {
    try {
        console.log('开始加载趋势数据，图表类型:', chartType);
        const response = await fetch('/api/trends');

        if (!response.ok) {
            throw new Error(`API错误: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log('趋势数据加载成功:', data);

        const chartDom = document.getElementById('trendsChart');
        if (!chartDom) {
            console.error('找不到 trendsChart 容器');
            return;
        }

        // 销毁旧图表实例
        if (trendsChartInstance && typeof trendsChartInstance.dispose === 'function') {
            try {
                trendsChartInstance.dispose();
            } catch (e) {
                console.warn('销毁旧图表失败:', e);
            }
        }

        // 清空容器
        chartDom.innerHTML = '';

        const myChart = echarts.init(chartDom);

        const years = Array.from({ length: 26 }, (_, i) => 1995 + i);
        const colors = ['#4a90e2', '#ef5350', '#66bb6a', '#ffa726', '#ab47bc'];
        const genres = ['pop', 'rock', 'hip-hop', 'electronic', 'r&b'];

        let option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: '#1a1f2e',
                borderColor: '#4a90e2',
                textStyle: { color: '#e0e6ed' },
            },
            legend: {
                top: 'bottom',
                textStyle: { color: '#e0e6ed' }
            },
            grid: { top: 20, right: 20, bottom: 50, left: 60, containLabel: true },
        };

        // ══════════════════════════════════
        // 折线图
        // ══════════════════════════════════
        if (chartType === 'line') {
            const series = [];
            genres.forEach((genre, idx) => {
                if (data[genre]) {
                    series.push({
                        name: data[genre].label,
                        type: 'line',
                        data: data[genre].data,
                        smooth: true,
                        lineStyle: { width: 2.5 },
                        itemStyle: { color: colors[idx] },
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: colors[idx] + '50' },
                                { offset: 1, color: colors[idx] + '00' }
                            ])
                        }
                    });
                }
            });

            option.xAxis = {
                type: 'category',
                data: years,
                axisLabel: { color: '#a8b2c1' },
                axisLine: { lineStyle: { color: '#2d3648' } }
            };
            option.yAxis = {
                type: 'value',
                axisLabel: { color: '#a8b2c1' },
                splitLine: { lineStyle: { color: '#2d3648' } }
            };
            option.series = series;
        }

        // ══════════════════════════════════
        // 柱状图
        // ══════════════════════════════════
        else if (chartType === 'bar') {
            const series = [];
            genres.forEach((genre, idx) => {
                if (data[genre]) {
                    series.push({
                        name: data[genre].label,
                        type: 'bar',
                        data: data[genre].data,
                        itemStyle: { color: colors[idx] }
                    });
                }
            });

            option.xAxis = {
                type: 'category',
                data: years,
                axisLabel: { color: '#a8b2c1' },
                axisLine: { lineStyle: { color: '#2d3648' } }
            };
            option.yAxis = {
                type: 'value',
                axisLabel: { color: '#a8b2c1' },
                splitLine: { lineStyle: { color: '#2d3648' } }
            };
            option.series = series;
        }

        // ══════════════════════════════════
        // 面积图
        // ══════════════════════════════════
        else if (chartType === 'area') {
            const series = [];
            genres.forEach((genre, idx) => {
                if (data[genre]) {
                    series.push({
                        name: data[genre].label,
                        type: 'line',
                        data: data[genre].data,
                        smooth: true,
                        stack: 'total',
                        lineStyle: { width: 2, color: colors[idx] },
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: colors[idx] + '80' },
                                { offset: 1, color: colors[idx] + '20' }
                            ])
                        }
                    });
                }
            });

            option.xAxis = {
                type: 'category',
                data: years,
                axisLabel: { color: '#a8b2c1' },
                axisLine: { lineStyle: { color: '#2d3648' } }
            };
            option.yAxis = {
                type: 'value',
                axisLabel: { color: '#a8b2c1' },
                splitLine: { lineStyle: { color: '#2d3648' } }
            };
            option.series = series;
        }

        // ══════════════════════════════════
        // 散点图
        // ══════════════════════════════════
        else if (chartType === 'scatter') {
            const series = [];
            genres.forEach((genre, idx) => {
                if (data[genre]) {
                    series.push({
                        name: data[genre].label,
                        type: 'scatter',
                        data: data[genre].data.map((v, i) => [i, v]),
                        symbolSize: 10,
                        itemStyle: { color: colors[idx], opacity: 0.7 }
                    });
                }
            });

            option.xAxis = {
                type: 'value',
                axisLabel: { color: '#a8b2c1' },
                axisLine: { lineStyle: { color: '#2d3648' } }
            };
            option.yAxis = {
                type: 'value',
                axisLabel: { color: '#a8b2c1' },
                axisLine: { lineStyle: { color: '#2d3648' } }
            };
            option.series = series;
        }

        // ══════════════════════════════════
        // 雷达图
        // ══════════════════════════════════
        else if (chartType === 'radar') {
            const yearLabels = years.map(y => y.toString());
            const series = [];

            genres.forEach((genre, idx) => {
                if (data[genre]) {
                    series.push({
                        name: data[genre].label,
                        value: data[genre].data,
                        areaStyle: { opacity: 0.3 },
                        itemStyle: { color: colors[idx] },
                        lineStyle: { color: colors[idx] }
                    });
                }
            });

            option = {
                backgroundColor: 'transparent',
                tooltip: { trigger: 'item', backgroundColor: '#1a1f2e', textStyle: { color: '#e0e6ed' } },
                legend: { textStyle: { color: '#e0e6ed' }, bottom: 20 },
                radar: {
                    indicator: yearLabels.map(year => ({ name: year, max: 100 })),
                    shape: 'polygon',
                    splitNumber: 4,
                    axisLine: { lineStyle: { color: '#2d3648' } },
                    splitLine: { lineStyle: { color: '#2d3648' } },
                    axisLabel: { color: '#a8b2c1' }
                },
                series: [{
                    type: 'radar',
                    data: series.map((s, idx) => ({
                        value: s.value,
                        name: genres[idx] ? data[genres[idx]].label : '',
                        itemStyle: { color: colors[idx] },
                        areaStyle: { opacity: 0.3 }
                    }))
                }]
            };
        }

        // ══════════════════════════════════
        // 热力图
        // ══════════════════════════════════
        else if (chartType === 'heatmap') {
            const heatmapData = [];
            genres.forEach((genre, genreIdx) => {
                if (data[genre]) {
                    data[genre].data.forEach((value, yearIdx) => {
                        heatmapData.push([yearIdx, genreIdx, value]);
                    });
                }
            });

            option.xAxis = {
                type: 'category',
                data: years,
                axisLabel: { color: '#a8b2c1' },
                axisLine: { lineStyle: { color: '#2d3648' } }
            };
            option.yAxis = {
                type: 'category',
                data: genres.map(g => data[g]?.label || g),
                axisLabel: { color: '#a8b2c1' },
                axisLine: { lineStyle: { color: '#2d3648' } }
            };
            option.visualMap = {
                min: 0,
                max: 100,
                calculable: true,
                inRange: {
                    color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
                },
                textStyle: { color: '#a8b2c1' }
            };
            option.series = [{
                name: '热度',
                type: 'heatmap',
                data: heatmapData,
                emphasis: { itemStyle: { borderColor: '#58a6ff', borderWidth: 2 } }
            }];
        }

        // ══════════════════════════════════
        // 漏斗图
        // ══════════════════════════════════
        else if (chartType === 'funnel') {
            const funnelData = genres.map((genre, idx) => {
                const avgValue = data[genre] ? Math.round(data[genre].data.reduce((a, b) => a + b) / data[genre].data.length) : 0;
                return {
                    value: avgValue,
                    name: data[genre]?.label || genre
                };
            }).sort((a, b) => b.value - a.value);

            option = {
                backgroundColor: 'transparent',
                tooltip: { backgroundColor: '#1a1f2e', textStyle: { color: '#e0e6ed' } },
                legend: { textStyle: { color: '#e0e6ed' }, bottom: 20 },
                series: [{
                    name: '平均热度',
                    type: 'funnel',
                    data: funnelData,
                    itemStyle: { borderColor: '#2d3648' }
                }]
            };
        }

        myChart.setOption(option);
        trendsChartInstance = myChart;
        window.addEventListener('resize', () => myChart.resize());
        console.log('图表已成功渲染');
    } catch (error) {
        console.error('加载趋势数据失败:', error);
        const chartDom = document.getElementById('trendsChart');
        if (chartDom) {
            chartDom.innerHTML = `<div style="color:#e0e6ed; padding:20px; text-align:center;">
                加载失败: ${error.message}
            </div>`;
        }
    }
}

async function loadRankings(year) {
    try {
        const response = await fetch(`/api/period/${year}`);
        const data = await response.json();

        const container = document.getElementById('rankingsContainer');
        container.innerHTML = '';

        if (data.top_10_songs && data.top_10_songs.length > 0) {
            currentPlaylist = data.top_10_songs;

            data.top_10_songs.forEach((song, idx) => {
                const item = document.createElement('div');
                item.className = 'ranking-item';

                const rankBadge = ['🥇', '🥈', '🥉'][idx] || `${idx + 1}`;
                const rankClass = idx < 3 ? 'ranking-number top-3' : 'ranking-number';

                // Generate Netease music link for global songs
                const neteaseUrl = `https://music.163.com/search/get?s=${encodeURIComponent(song.song + ' ' + song.artist)}&type=1`;

                item.innerHTML = `
                    <div class="${rankClass}">${rankBadge}</div>
                    <div class="ranking-info">
                        <div class="ranking-song">${song.song}</div>
                        <div class="ranking-artist">${song.artist}</div>
                    </div>
                    <div class="ranking-meta">
                        <span class="ranking-genre">${song.genre}</span>
                        <span class="ranking-popularity">热度: ${song.popularity}/100</span>
                    </div>
                    <div class="play-icon" onclick="window.open('${neteaseUrl}', '_blank')" title="在网易云打开">▶</div>
                `;

                container.appendChild(item);
            });
        }
    } catch (error) {
        console.error('加载排行榜失败:', error);
    }
}

// ═══════════════════════════════════════════════════
// 中国音乐数据加载
// ═══════════════════════════════════════════════════

async function loadChinaTrends(chartType = 'line') {
    try {
        // Fetch genre distribution data instead of trends
        const response = await fetch('/api/china/genre-distribution');
        const data = await response.json();

        const chartDom = document.getElementById('chinaTrendsChart');

        // 销毁旧图表实例
        if (chinaTrendsChartInstance && typeof chinaTrendsChartInstance.dispose === 'function') {
            try {
                chinaTrendsChartInstance.dispose();
            } catch (e) {
                console.warn('销毁旧图表失败:', e);
            }
        }

        // 清空容器
        chartDom.innerHTML = '';

        const myChart = echarts.init(chartDom);

        // Chart names mapping
        const chartNames = ['热歌榜', '新歌榜', '飙升榜', '原创榜'];
        const chartKeys = ['hot', 'new', 'rising', 'original'];
        const colors = ['#4a90e2', '#ef5350', '#66bb6a', '#ffa726', '#ab47bc', '#29b6f6', '#ec407a'];

        // Collect all unique genres
        const allGenres = new Set();
        for (const chartKey in data) {
            for (const genre in data[chartKey]) {
                allGenres.add(genre);
            }
        }
        const genres = Array.from(allGenres).sort();

        // Build series data: each genre is a series
        const series = [];
        let genreIdx = 0;

        for (const genre of genres) {
            if (genreIdx >= colors.length) break;

            const genreData = [];
            for (const chartKey of chartKeys) {
                const count = data[chartKey] && data[chartKey][genre] ? data[chartKey][genre] : 0;
                genreData.push(count);
            }

            const seriesItem = {
                name: genre.charAt(0).toUpperCase() + genre.slice(1),
                type: chartType === 'line' ? 'bar' : chartType,
                data: genreData,
                itemStyle: { color: colors[genreIdx] }
            };

            if (chartType === 'bar') {
                seriesItem.type = 'bar';
            }

            series.push(seriesItem);
            genreIdx++;
        }

        let option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: '#1a1f2e',
                borderColor: '#4a90e2',
                textStyle: { color: '#e0e6ed' },
                axisPointer: { type: 'shadow' }
            },
            grid: {
                top: 20,
                right: 20,
                bottom: 50,
                left: 60,
                containLabel: true
            },
            legend: {
                top: 'bottom',
                textStyle: { color: '#e0e6ed' }
            }
        };

        // Customize based on chart type
        if (chartType === 'bar' || chartType === 'line') {
            option.xAxis = {
                type: 'category',
                data: chartNames,
                axisLabel: { color: '#a8b2c1', fontSize: 12 },
                axisLine: { lineStyle: { color: '#2d3648' } }
            };
            option.yAxis = {
                type: 'value',
                axisLabel: { color: '#a8b2c1' },
                splitLine: { lineStyle: { color: '#2d3648' } },
                name: '歌曲数量'
            };

            // Update series for line chart
            if (chartType === 'line') {
                for (let i = 0; i < series.length; i++) {
                    series[i].type = 'line';
                    series[i].smooth = true;
                    series[i].lineStyle = { width: 2.5 };
                    series[i].areaStyle = {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: colors[i % colors.length] + '50' },
                            { offset: 1, color: colors[i % colors.length] + '00' }
                        ])
                    };
                }
            }

            option.series = series;
        } else if (chartType === 'radar') {
            // Radar chart configuration
            const radarIndicators = chartNames.map(name => ({
                name: name,
                max: 10
            }));

            const radarSeries = genres.map((genre, idx) => {
                const genreData = [];
                for (const chartKey of chartKeys) {
                    const count = data[chartKey] && data[chartKey][genre] ? data[chartKey][genre] : 0;
                    genreData.push(count);
                }
                return {
                    name: genre.charAt(0).toUpperCase() + genre.slice(1),
                    value: genreData,
                    areaStyle: { opacity: 0.3 },
                    itemStyle: { color: colors[idx % colors.length] },
                    lineStyle: { color: colors[idx % colors.length] }
                };
            });

            option.radar = {
                indicator: radarIndicators,
                shape: 'polygon',
                splitNumber: 4,
                axisLine: { lineStyle: { color: '#2d3648' } },
                splitLine: { lineStyle: { color: '#2d3648' } },
                axisLabel: { color: '#a8b2c1' }
            };

            option.series = [{
                name: '',
                type: 'radar',
                data: radarSeries
            }];
        }

        myChart.setOption(option);
        chinaTrendsChartInstance = myChart;
        window.addEventListener('resize', () => myChart.resize());
    } catch (error) {
        console.error('加载中国音乐趋势失败:', error);
    }
}

async function loadChinaRankings(chartType) {
    try {
        // Map chart types to month numbers for API
        const chartToMonth = {
            'hot': 1,
            'new': 2,
            'rising': 3,
            'original': 4
        };

        const month = chartToMonth[chartType] || 1;
        const response = await fetch(`/api/china/rankings/${month}`);
        const songs = await response.json();

        const container = document.getElementById('chinaRankingsContainer');
        container.innerHTML = '';

        if (Array.isArray(songs) && songs.length > 0) {
            songs.forEach((song, idx) => {
                const item = document.createElement('div');
                item.className = 'ranking-item';

                const rankBadge = ['🥇', '🥈', '🥉'][idx] || `${idx + 1}`;
                const rankClass = idx < 3 ? 'ranking-number top-3' : 'ranking-number';

                // Generate Netease music link
                const neteaseUrl = song.song_id
                    ? `https://music.163.com/song?id=${song.song_id}`
                    : `https://music.163.com/search/get?s=${encodeURIComponent(song.song + ' ' + song.artist)}&type=1`;

                item.innerHTML = `
                    <div class="${rankClass}">${rankBadge}</div>
                    <div class="ranking-info">
                        <div class="ranking-song">${song.song}</div>
                        <div class="ranking-artist">${song.artist}</div>
                    </div>
                    <div class="ranking-meta">
                        <span class="ranking-genre">${song.genre}</span>
                        <span class="ranking-popularity">热度: ${song.popularity}/100</span>
                    </div>
                    <div class="play-icon" onclick="window.open('${neteaseUrl}', '_blank')" title="在网易云打开">▶</div>
                `;

                container.appendChild(item);
            });
        }
    } catch (error) {
        console.error('加载中国排行榜失败:', error);
    }
}

async function loadChinaStats() {
    try {
        const response = await fetch('/api/china/stats');
        const stats = await response.json();

        const container = document.getElementById('chinaStatsContainer');
        container.innerHTML = '';

        for (const genre in stats) {
            const stat = stats[genre];
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.innerHTML = `
                <div class="stat-genre">${genre}</div>
                <div class="stat-value">${stat.avg_popularity}</div>
                <div class="stat-label">平均热度（${stat.count}首）</div>
            `;
            container.appendChild(card);
        }
    } catch (error) {
        console.error('加载中国统计失败:', error);
    }
}

// ═══════════════════════════════════════════════════
// 音乐播放器
// ═══════════════════════════════════════════════════

function playSong(title, artist, genre) {
    const modal = document.getElementById('playerModal');
    modal.classList.add('show');

    document.getElementById('playerSongTitle').textContent = title;
    document.getElementById('playerArtist').textContent = artist;
    document.getElementById('playerGenre').textContent = typeof genre === 'string' ? genre.toUpperCase() : '未知';

    const colorHash = Math.abs(hashCode(title + artist)) % 360;
    document.getElementById('coverArt').style.background =
        `linear-gradient(135deg, hsl(${colorHash}, 70%, 50%), hsl(${colorHash + 60}, 70%, 50%))`;

    isPlaying = true;
    document.getElementById('playBtn').classList.add('playing');
}

function togglePlay() {
    const btn = document.getElementById('playBtn');
    isPlaying = !isPlaying;
    btn.textContent = isPlaying ? '⏸' : '▶';
    btn.classList.toggle('playing');
}

function playPrev() {
    currentTrackIndex = (currentTrackIndex - 1 + currentPlaylist.length) % currentPlaylist.length;
    const track = currentPlaylist[currentTrackIndex];
    if (track) {
        playSong(track.song, track.artist, track.genre);
    }
}

function playNext() {
    currentTrackIndex = (currentTrackIndex + 1) % currentPlaylist.length;
    const track = currentPlaylist[currentTrackIndex];
    if (track) {
        playSong(track.song, track.artist, track.genre);
    }
}

function closePlayer() {
    document.getElementById('playerModal').classList.remove('show');
    isPlaying = false;
}

function addToPlaylist() {
    const title = document.getElementById('playerSongTitle').textContent;
    alert('已收藏: ' + title);
}

function shareTrack() {
    const title = document.getElementById('playerSongTitle').textContent;
    const artist = document.getElementById('playerArtist').textContent;
    const text = `我在听《${title}》by ${artist} 🎵`;

    if (navigator.share) {
        navigator.share({
            title: '大众金曲',
            text: text,
            url: window.location.href
        });
    } else {
        alert(text);
    }
}

function goBack() {
    window.location.href = '/';
}

function hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return hash;
}

window.onclick = function(event) {
    const modal = document.getElementById('playerModal');
    if (event.target == modal) {
        closePlayer();
    }
}
