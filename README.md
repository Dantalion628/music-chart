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

## 🚀 快速开始（本地运行）

### 1. 环境准备

```bash
cd music-charts
pip install -r requirements.txt
```

### 2. 生成数据

如果数据已存在：
```bash
python app.py
```

如果需要生成演示数据：
```bash
python generate_demo.py
python app.py
```

### 3. 访问应用

打开浏览器访问：`http://localhost:5000`

## 🌐 部署到 Render

### 1. 关联 GitHub 仓库

```bash
git remote add origin <你的GitHub仓库URL>
git push -u origin master
```

### 2. 在 Render 创建新服务

1. 访问 https://render.com
2. 点击 "New +" → "Web Service"
3. 连接你的 GitHub 账户
4. 选择 `music-charts` 仓库
5. 填写配置：
   - **Name**: `music-charts` (或你喜欢的名字)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python generate_demo.py`
   - **Start Command**: `gunicorn app:app`

### 3. 部署

点击 "Create Web Service"，Render 会自动部署。等待部署完成，你会得到一个类似 `music-charts-xxxx.onrender.com` 的 URL。

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

## 🎨 自定义

### 修改颜色方案

编辑 `static/css/style.css` 中的 CSS 变量：

```css
:root {
    --bg-dark: #0f1419;
    --accent-blue: #4a90e2;
    /* ... 其他颜色 */
}
```

### 修改数据

1. 替换 `processed_data.csv` 为你的数据文件
2. 确保 CSV 包含列: `year, date, rank, song, artist, genre, popularity`

## ⚠️ 常见问题

**Q: 无法从 GitHub 获取数据？**  
A: 脚本会自动使用演示数据。演示数据基于真实市场统计，可用于演示。

**Q: Render 部署失败？**  
A: 检查 `build.sh` 和 `generate_demo.py` 是否可以在没有网络的情况下运行。

**Q: 如何更新真实数据？**  
A: 修改 `fetch_and_process_data.py` 的数据源，或直接替换 `processed_data.csv`。

## 📝 许可证

MIT License

---

**🌟 Made with ❤️ for music lovers**
