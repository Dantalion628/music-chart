// 当前选中的年份
let currentYear = 1995;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 标签页切换
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', switchTab);
    });

    // 年份选择
    document.querySelectorAll('.year-btn').forEach(btn => {
        btn.addEventListener('click', selectYear);
    });

    // 加载数据
    loadPeriods();
    loadTrends();
    loadRankings(1995);
});

// 切换标签页
function switchTab(e) {
    const tabName = e.target.dataset.tab;

    // 更新按钮状态
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');

    // 显示/隐藏内容
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');

    // 刷新图表（如果是趋势标签）
    if (tabName === 'trends') {
        setTimeout(() => {
            window.trendsChart?.resize();
        }, 100);
    }
}

// 加载五年周期数据
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

// 创建周期卡片
function createPeriodCard(period) {
    const card = document.createElement('div');
    card.className = 'period-card';

    let genresHtml = '';
    period.genres.forEach((genre, index) => {
        genresHtml += `
            <div class="genre-item">
                <span class="genre-name">${index + 1}. ${genre.name}</span>
                <span class="genre-count">${genre.count}首</span>
            </div>
        `;

        if (genre.sample_songs && genre.sample_songs.length > 0) {
            genresHtml += '<div class="sample-songs">';
            genre.sample_songs.forEach(song => {
                genresHtml += `
                    <div class="sample-song">
                        <span class="sample-song-title">${song.song}</span>
                        <br><small>${song.artist}</small>
                    </div>
                `;
            });
            genresHtml += '</div>';
        }
    });

    card.innerHTML = `
        <div class="period-year">${period.year}</div>
        <div class="period-range">${period.period}年</div>
        ${genresHtml}
    `;

    return card;
}

// 加载流派趋势
async function loadTrends() {
    try {
        const response = await fetch('/api/trends');
        const data = await response.json();

        const chartDom = document.getElementById('trendsChart');
        const myChart = echarts.init(chartDom, null, { renderer: 'canvas' });

        // 准备数据
        const years = Array.from({ length: 26 }, (_, i) => 1995 + i);
        const series = [];

        const colors = ['#4a90e2', '#ef5350', '#66bb6a', '#ffa726', '#ab47bc'];
        const genres = ['pop', 'rock', 'hip-hop', 'electronic', 'r&b'];

        genres.forEach((genre, idx) => {
            if (data[genre]) {
                series.push({
                    name: data[genre].label,
                    type: 'line',
                    data: data[genre].data,
                    smooth: true,
                    lineStyle: { width: 2 },
                    itemStyle: { borderWidth: 0 },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: colors[idx] + '40' },
                            { offset: 1, color: colors[idx] + '00' }
                        ])
                    },
                    color: colors[idx]
                });
            }
        });

        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: '#1a1f2e',
                borderColor: '#4a90e2',
                textStyle: { color: '#e0e6ed' },
                formatter: (params) => {
                    let result = params[0].axisValue + '年<br/>';
                    params.forEach(p => {
                        result += `<span style="color: ${p.color}">● ${p.seriesName}: ${p.value}</span><br/>`;
                    });
                    return result;
                }
            },
            grid: {
                top: 20,
                right: 20,
                bottom: 50,
                left: 60,
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: years,
                boundaryGap: false,
                axisLabel: { color: '#a8b2c1' },
                axisLine: { lineStyle: { color: '#2d3648' } }
            },
            yAxis: {
                type: 'value',
                axisLabel: { color: '#a8b2c1' },
                splitLine: { lineStyle: { color: '#2d3648' } }
            },
            series: series,
            legend: {
                top: 'bottom',
                textStyle: { color: '#e0e6ed' }
            }
        };

        myChart.setOption(option);
        window.trendsChart = myChart;

        // 响应式
        window.addEventListener('resize', () => myChart.resize());

    } catch (error) {
        console.error('加载趋势数据失败:', error);
    }
}

// 选择年份
function selectYear(e) {
    const year = parseInt(e.target.dataset.year);
    currentYear = year;

    // 更新按钮状态
    document.querySelectorAll('.year-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');

    // 加载排行榜
    loadRankings(year);
}

// 加载排行榜数据
async function loadRankings(year) {
    try {
        const response = await fetch(`/api/period/${year}`);
        const data = await response.json();

        const table = document.getElementById('rankingsTable');
        table.innerHTML = '';

        // 创建表头
        const header = document.createElement('div');
        header.className = 'ranking-row';
        header.style.background = '#2d3648';
        header.style.fontWeight = 'bold';
        header.innerHTML = `
            <div style="width: 50px; text-align: center;">排名</div>
            <div style="flex: 1;">歌曲信息</div>
            <div>流派</div>
            <div>热度</div>
        `;
        table.appendChild(header);

        // 创建数据行
        data.top_10_songs.forEach((song, idx) => {
            const row = document.createElement('div');
            row.className = 'ranking-row';

            const rankClass = idx < 3 ? 'ranking-number top-3' : 'ranking-number';
            const rankBadge = ['🥇', '🥈', '🥉'][idx] || `${idx + 1}`;

            row.innerHTML = `
                <div class="ranking-number">${rankBadge}</div>
                <div class="ranking-info">
                    <div class="ranking-song">${song.song}</div>
                    <div class="ranking-artist">${song.artist}</div>
                </div>
                <div>
                    <span class="ranking-genre">${song.genre}</span>
                </div>
                <div class="ranking-popularity">${song.popularity}/100</div>
            `;

            table.appendChild(row);
        });
    } catch (error) {
        console.error('加载排行榜失败:', error);
    }
}
