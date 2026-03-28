import requests
import json
import os

def fetch_polymarket_data():
    print("🚀 PolyAxiom 终极高胜率引擎启动...")
    # 抓取前 100 个活跃事件
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"

    # 1. 加载旧数据用于计算异动
    old_data = {}
    if os.path.exists('data.json'):
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                old_list = json.load(f)
                old_data = {item['title']: item['odds'] for item in old_list}
        except: pass

    signals = []
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()

        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets or not title: continue
            
            m = markets[0]
            try:
                prices = m.get('outcomePrices')
                odds_list = json.loads(prices) if isinstance(prices, str) else prices
                odds = round(float(odds_list[0]) * 100, 1)
                # 过滤极低胜率噪音
                if odds < 5: continue
            except: continue

            # 交易量补全
            v24 = float(event.get('volume24h', 0))
            v_event = float(event.get('volume', 0))
            final_vol = max(v24, v_event)

            # 异动检测：赔率波动 >= 5% 或 成交量 >= 5000 刀
            is_hot = False
            if title in old_data:
                change = abs(odds - old_data[title])
                if change >= 5: is_hot = True
            if final_vol >= 5000: is_hot = True

            signals.append({
                "title": title,
                "odds": odds,
                "volume": round(final_vol / 1000, 1),
                "is_hot": is_hot,
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom",
                "category": event.get('groupItemTitle', '预测市场')
            })

        # 排序：异动项目 > 90%胜率 > 普通项目
        signals.sort(key=lambda x: (x['is_hot'], x['odds'] >= 90, x['odds']), reverse=True)

        # 写入 data.json (保留前 40 条)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)

        # --- SEO 增强：自动生成 Sitemap.xml ---
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sitemap_content += '  <url><loc>https://polyaxiom.com/</loc><priority>1.0</priority></url>\n'
        for s in signals[:30]:
            safe_link = s['link'].replace('&', '&amp;')
            sitemap_content += f'  <url><loc>{safe_link}</loc><changefreq>hourly</changefreq></url>\n'
        sitemap_content += '</urlset>'
        
        with open('sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
            
        print(f"✅ 更新完成：数据与 Sitemap.xml 已同步推送到云端。")

    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()
