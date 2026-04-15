// 应用状态
let currentYear = 1995;
let currentPlaylist = [];
let currentTrackIndex = 0;
let isPlaying = false;
let spotifyAccessToken = null;

// Spotify 配置（需要替换为你的凭证）
const SPOTIFY_CLIENT_ID = 'YOUR_CLIENT_ID';
const SPOTIFY_REDIRECT_URI = window.location.origin + '/callback';

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupYearSelector();
    loadPeriods();
    loadTrends();
    loadRankings(1995);

    // 尝试从URL获取Spotify token
    const hash = window.location.hash;
    if (hash) {
        const token = new URLSearchParams(hash.substring(1)).get('access_token');
        if (token) {
            spotifyAccessToken = token;
            localStorage.setItem('spotifyToken', token);
        }
    }
});

// 导航切换
function setupNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', switchTab);
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
            window.trendsChart?.resize();
        }, 100);
    }
}

// 年份选择
function setupYearSelector() {
    document.querySelectorAll('.year-btn').forEach(btn => {
        btn.addEventListener('click', selectYear);
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

// 加载5年周期数据
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

    // 添加代表歌曲
    if (period.genres[0] && period.genres[0].sample_songs) {
        genresHtml += '<div class="sample-songs"><strong>代表歌曲：</strong>';
        period.genres[0].sample_songs.forEach(song => {
            genresHtml += `
                <div class="sample-song" onclick="playSong('${song.song}', '${song.artist}', '${song.popularity}')">
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

// 加载流派趋势
async function loadTrends() {
    try {
        const response = await fetch('/api/trends');
        const data = await response.json();

        const chartDom = document.getElementById('trendsChart');
        const myChart = echarts.init(chartDom);

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
        window.addEventListener('resize', () => myChart.resize());
    } catch (error) {
        console.error('加载趋势数据失败:', error);
    }
}

// 加载排行榜
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
                    <div class="play-icon" onclick="playSong('${song.song}', '${song.artist}', '${song.genre}')">▶</div>
                `;

                container.appendChild(item);
            });
        }
    } catch (error) {
        console.error('加载排行榜失败:', error);
    }
}

// 播放歌曲
function playSong(title, artist, genre) {
    const modal = document.getElementById('playerModal');
    modal.classList.add('show');

    document.getElementById('playerSongTitle').textContent = title;
    document.getElementById('playerArtist').textContent = artist;
    document.getElementById('playerGenre').textContent = genre.toUpperCase();

    // 生成封面艺术
    const colorHash = Math.abs(hashCode(title + artist)) % 360;
    document.getElementById('coverArt').style.background =
        `linear-gradient(135deg, hsl(${colorHash}, 70%, 50%), hsl(${colorHash + 60}, 70%, 50%))`;

    // 模拟播放
    isPlaying = true;
    document.getElementById('playBtn').classList.add('playing');

    // 如果有Spotify token，搜索真实歌曲
    if (spotifyAccessToken) {
        searchSpotifyTrack(title, artist);
    }
}

// 搜索Spotify歌曲
async function searchSpotifyTrack(title, artist) {
    try {
        const response = await fetch(
            `https://api.spotify.com/v1/search?q=track:${title} artist:${artist}&type=track&limit=1`,
            {
                headers: {
                    'Authorization': 'Bearer ' + spotifyAccessToken
                }
            }
        );

        const data = await response.json();
        if (data.tracks && data.tracks.items.length > 0) {
            const track = data.tracks.items[0];
            // 这里可以添加播放功能
            console.log('Found track:', track);
        }
    } catch (error) {
        console.error('Spotify搜索失败:', error);
    }
}

// 播放/暂停
function togglePlay() {
    const btn = document.getElementById('playBtn');
    isPlaying = !isPlaying;
    btn.textContent = isPlaying ? '⏸' : '▶';
    btn.classList.toggle('playing');
}

// 上一首
function playPrev() {
    currentTrackIndex = (currentTrackIndex - 1 + currentPlaylist.length) % currentPlaylist.length;
    const track = currentPlaylist[currentTrackIndex];
    if (track) {
        playSong(track.song, track.artist, track.genre);
    }
}

// 下一首
function playNext() {
    currentTrackIndex = (currentTrackIndex + 1) % currentPlaylist.length;
    const track = currentPlaylist[currentTrackIndex];
    if (track) {
        playSong(track.song, track.artist, track.genre);
    }
}

// 关闭播放器
function closePlayer() {
    document.getElementById('playerModal').classList.remove('show');
    isPlaying = false;
}

// 收藏
function addToPlaylist() {
    const title = document.getElementById('playerSongTitle').textContent;
    alert('已收藏: ' + title);
    // 这里可以保存到localStorage
}

// 分享
function shareTrack() {
    const title = document.getElementById('playerSongTitle').textContent;
    const artist = document.getElementById('playerArtist').textContent;
    const text = `我在听《${title}》by ${artist}，来自"大众金曲"🎵`;

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

// 返回首页
function goBack() {
    window.location.href = '/';
}

// 字符串Hash函数
function hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return hash;
}

// 点击外部关闭模态框
window.onclick = function(event) {
    const modal = document.getElementById('playerModal');
    if (event.target == modal) {
        closePlayer();
    }
}
