<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PolyAxiom - Polymarket 实时高胜率信号监控</title>
    
    <meta name="description" id="meta-description" content="聚焦 Polymarket 实时高胜率信号，捕捉预测市场每一个机会。">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@Poly_Axiom">
    <meta name="twitter:image" content="https://polyaxiom.com/logo.png">

    <style>
        :root {
            --bg: #0a0e17;
            --card-bg: #161b22;
            --accent: #238636;
            --text: #adbac7;
            --text-bright: #ffffff;
            --text-dim: #768390;
            --link: #58a6ff;
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: -apple-system, system-ui, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        header {
            text-align: center;
            margin-bottom: 25px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .logo-container img {
            max-width: 130px; /* 维持 130px 比例 */
            height: auto;
            filter: drop-shadow(0 0 8px rgba(88, 166, 255, 0.2));
            margin-bottom: 8px;
        }

        header p { font-size: 13px; color: var(--text-dim); margin: 0; }

        .container {
            max-width: 1200px;
            width: 100%;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }

        .card {
            background: var(--card-bg);
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s;
        }

        .card:hover { transform: translateY(-3px); border-color: #444c56; }

        .title {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-bright);
            margin-bottom: 15px;
            min-height: 44px; /* 保持整齐 */
            line-height: 1.4;
        }

        .odds-value { font-size: 22px; font-weight: bold; color: var(--link); }

        .stats-box {
            background: rgba(255,255,255,0.03);
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 15px;
        }

        .btn {
            background: var(--accent);
            color: white;
            text-align: center;
            padding: 10px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
        }

        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

        footer {
            margin-top: 60px;
            padding: 30px;
            text-align: center;
            font-size: 12px;
            color: var(--text-dim);
            border-top: 1px solid #30363d;
            width: 100%;
        }

        .footer-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 10px;
        }

        .footer-links a { color: var(--link); text-decoration: none; }
    </style>
</head>
<body>

<header>
    <div class="logo-container">
        <img src="logo.png" alt="PolyAxiom">
    </div>
    <p>Polymarket 实时高胜率信号监控</p>
</header>

<div class="container" id="signals-list">
    <p style="grid-column: 1/-1; text-align:center;">正在接入实时数据流...</p>
</div>

<footer>
    <div>© 2026 PolyAxiom | 聚焦预测市场热度</div>
    <div class="footer-links">
        <a href="https://t.me/XXYY_CC" target="_blank">✈️ Telegram</a>
        <a href="https://x.com/Poly_Axiom" target="_blank">𝕏 Twitter</a>
    </div>
</footer>

<script>
    async function loadSignals() {
        try {
            // 使用新时间戳强制刷新
            const response = await fetch('data.json?v=' + Date.now());
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            const list = document.getElementById('signals-list');
            
            list.innerHTML = data.map(item => `
                <div class="card">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 11px; color: var(--link); text-transform: uppercase;">${item.category}</span>
                            <span style="font-size: 10px; color: #3fb950; display: flex; align-items: center;">
                                <span style="width: 6px; height: 6px; background: #3fb950; border-radius: 50%; margin-right: 5px; animation: pulse 2s infinite;"></span>
                                Vol: $${item.volume || 0}k
                            </span>
                        </div>
                        <div class="title">${item.title}</div>
                        <div class="stats-box">
                            <div style="font-size: 11px; color: var(--text-dim); margin-bottom: 4px;">当前胜率</div>
                            <div class="odds-value">${item.odds}%</div>
                        </div>
                    </div>
                    <a href="${item.link}" class="btn" target="_blank">立即前往下单</a>
                </div>
            `).join('');
            
            // 自动更新 SEO
            const topTitles = data.slice(0, 3).map(item => item.title).join(', ');
            document.getElementById('meta-description').content = `正在监控：${topTitles}...`;
        } catch (e) {
            console.error("加载失败:", e);
            document.getElementById('signals-list').innerHTML = '<p style="grid-column: 1/-1; text-align:center;">数据更新中，请稍后刷新...</p>';
        }
    }
    loadSignals();
    setInterval(loadSignals, 60000); // 每分钟自动刷新
</script>
</body>
</html>
