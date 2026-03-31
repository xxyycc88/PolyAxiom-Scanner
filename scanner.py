import requests
import json
import os
import random

def fetch_polymarket_data():
    print("🚀 PolyAxiom 数据修复扫描中...")
    # 使用更稳定的 API 路径
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"
    BASE_URL = "https://polyaxiom.com/"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        signals = []

        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets or not title: continue
            
            # 锁定第一个有效市场
            m = markets[0]
            try:
                prices_raw = m.get('outcomePrices')
                # 兼容字符串或列表格式
                prices = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
                
                if not prices or len(prices) == 0:
                    continue
                
                # 获取主选项胜率并转为百分比
                odds_val = float(prices[0])
                # 🛠️ 核心修复：胜率为 0 或过低的项目直接剔除，防止出现 0% 尴尬界面
                if odds_val <= 0.01: 
                    continue
                    
                odds = round(odds_val * 100, 1)
            except (ValueError, TypeError, IndexError):
                continue

            v_event = float(event.get('volume', 0))
            # 只有成交额大于 5000 且胜率有效的才标记为 HOT
            is_hot = True if v_event > 5000 and odds > 5 else False

            signals.append({
                "title": title,
                "odds": odds,
                "volume": round(v_event / 1000, 1),
                "is_hot": is_hot,
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom",
                "rand_score": random.uniform(0, 10)
            })

        # 排序：异动项目强行置顶，其余按随机洗牌确保页面活性
        signals.sort(key=lambda x: (x['is_hot'], x['rand_score']), reverse=True)

        # 保存前 40 个最优质的项目
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)

        # 同步生成符合 Google 要求的 Sitemap
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sitemap += f'  <url><loc>{BASE_URL}</loc><priority>1.0</priority></url>\n</urlset>'
        with open('sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap)
            
        print(f"✅ 同步完成，有效信号数量: {len(signals)}")

    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()
