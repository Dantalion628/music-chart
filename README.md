# 🎵 大众金曲流行度分析 | Music Popularity Analysis 1995-2020

一个交互式数据可视化网站，展示 1995-2020 年间 5 大音乐流派（Pop、Rock、Hip-Hop、Electronic、R&B）的流行度趋势和排行榜排名。

## 📊 功能特性

- **五年周期分析** - 每个 5 年周期的最流行音乐类型统计
- **流派趋势图表** - 1995-2020 年 5 大流派流行度变化曲线
- **排行榜排行** - 每个关键年份（1995、2000...2020）的前 10 热曲
- **响应式设计** - 低饱和蓝色主题，暗黑美学

## 🛠 技术栈

- **后端**: Flask 2.3.0
- **前端**: ECharts 5 + 原生 JavaScript
- **数据源**: Billboard Hot 100 (GitHub) 或演示数据
- **部署**: Render.com

## 📁 项目结构

```
music-charts/
├── app.py                      # Flask 主应用
├── fetch_and_process_data.py  # 数据爬取和处理
├── generate_demo.py            # 生成演示数据（无网络连接时使用）
├── processed_data.csv          # 处理后的数据文件
├── requirements.txt            # Python 依赖
├── Procfile                    # Render 部署配置
├── build.sh                    # 构建脚本
├── templates/
│   └── index.html             # HTML 模板
└── static/
    ├── css/style.css          # 样式表
    └── js/main.js             # 前端交互逻辑
```


## 📊 数据信息

### 数据来源

- **主要数据**: Billboard Hot 100 (GitHub: mhollingshead/billboard-hot-100)
- **备选方案**: 内置演示数据（基于真实市场统计）

### 数据范围

- **时间**: 1995-2020 年
- **流派**: Pop、Rock、Hip-Hop、Electronic、R&B
- **指标**: 流行度分数（0-100）

## 🔧 API 端点

| 端点 | 方法 | 描述 |
|-----|------|------|
| `/` | GET | 主页面 |
| `/api/periods` | GET | 获取所有 5 年周期数据 |
| `/api/period/<year>` | GET | 获取特定年份前 10 排行 |
| `/api/trends` | GET | 获取 5 大流派趋势数据 |



---

**🌟 Made with ❤️ for music lovers**
