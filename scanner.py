import requests
import json
import os
import random

def fetch_polymarket_data():
    print("🚀 PolyAxiom 后台扫描中...")
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"
    BASE_URL = "https://polyaxiom.com/"

    try:
        response = requests.get(url, timeout=20)
        data = response.json()
        signals = []

        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets: continue
            
            m = markets[0]
            try:
                prices = m.get('outcomePrices')
                odds_list = json.loads(prices) if isinstance(prices, str) else prices
                odds = round(float(odds_list[0]) * 100, 1)
            except: continue

            v_event = float(event.get('volume', 0))
            is_hot = True if v_event > 5000 else False

            signals.append({
                "title": title,
                "odds": odds,
                "volume": round(v_event / 1000, 1),
                "is_hot": is_hot,
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom",
                "rand_score": random.uniform(0, 10)
            })

        # 排序与洗牌
        signals.sort(key=lambda x: (x['is_hot'], x['rand_score']), reverse=True)

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)

        # ✅ 生成 SEO Sitemap
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sitemap += f'  <url><loc>{BASE_URL}</loc><priority>1.0</priority></url>\n</urlset>'
        with open('sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap)
            
        print("✅ 后台同步完成")

    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()
