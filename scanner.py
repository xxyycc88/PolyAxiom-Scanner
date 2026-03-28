import requests
import json
import os
from datetime import datetime

def fetch_polymarket_data():
    print("🚀 PolyAxiom 动态热度扫描启动...")
    # 增加 limit 到 50，扩大筛选池
    url = "https://gamma-api.polymarket.com/events?limit=50&active=true&closed=false"
    
    signals = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets or not title: continue
            
            m = markets[0]
            # 抓取胜率和交易量
            prices = m.get('outcomePrices')
            volume = float(event.get('volume24h', 0)) # 24小时交易量
            
            try:
                odds = float(json.loads(prices)[0]) if isinstance(prices, str) else float(prices[0])
                if 0 < odds <= 1.0: odds *= 100
            except: continue
            
            link = f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": round(odds, 1),
                "volume": round(volume / 1000, 1), # 转换为 k 为单位
                "link": link,
                "category": event.get('groupItemTitle', '预测市场'),
                "last_update": datetime.now().strftime('%H:%M')
            })
            
        # --- 核心逻辑：混合排序 ---
        # 逻辑：优先展示 交易量 > 10k 且 胜率 > 50% 的热门项目
        # 这样即使胜率不是最高的，但只要有人在疯狂交易（暴涨），就会排在前面
        signals.sort(key=lambda x: (x['volume'] > 10, x['odds']), reverse=True)
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:30], f, ensure_ascii=False, indent=4)
            
        # 自动更新 SEO 文件
        generate_seo_files()
        print(f"✅ 成功更新 {len(signals)} 条信号，包含交易量权重。")
        
    except Exception as e:
        print(f"❌ 运行报错: {e}")

def generate_seo_files():
    robots_content = "User-agent: *\nAllow: /\nSitemap: https://polyaxiom.com/sitemap.xml"
    with open('robots.txt', 'w') as f: f.write(robots_content)
    now = datetime.now().strftime('%Y-%m-%d')
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://polyaxiom.com/</loc><lastmod>{now}</lastmod><changefreq>hourly</changefreq><priority>1.0</priority></url>
</urlset>"""
    with open('sitemap.xml', 'w') as f: f.write(sitemap_content)

if __name__ == "__main__":
    fetch_polymarket_data()
