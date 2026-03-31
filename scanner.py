import requests
import json
import os
import random

def fetch_polymarket_data():
    print("🚀 PolyAxiom 紧急修复扫描中...")
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"
    
    try:
        response = requests.get(url, timeout=20)
        data = response.json()
        signals = []

        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets or not title: continue
            
            m = markets[0]
            try:
                prices_raw = m.get('outcomePrices')
                prices = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
                
                # ✅ 核心修复 1：如果没有价格数据，直接跳过，不存入数据文件
                if not prices or len(prices) == 0:
                    continue
                
                odds_val = float(prices[0])
                
                # ✅ 核心修复 2：如果胜率接近 0（比如低于 0.5%），视为无效僵尸项目，直接跳过
                if odds_val < 0.005: 
                    continue
                    
                odds = round(odds_val * 100, 1)
            except:
                continue

            v_event = float(event.get('volume', 0))
            # 只有成交额 > 2000 且胜率正常的才标记为异动
            is_hot = True if v_event > 2000 and odds > 5 else False

            signals.append({
                "title": title,
                "odds": odds,
                "volume": round(v_event / 1000, 1),
                "is_hot": is_hot,
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom",
                "rand_score": random.uniform(0, 10)
            })

        # 排序逻辑：热门项目排最前，其次随机洗牌
        signals.sort(key=lambda x: (x['is_hot'], x['rand_score']), reverse=True)

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)
            
        print(f"✅ 修复完成，过滤后的有效信号数: {len(signals)}")

    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()
