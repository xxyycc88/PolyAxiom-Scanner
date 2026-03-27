import requests
import json
import os

def fetch_polymarket_data():
    print("🔍 PolyAxiom 数据同步开始...")
    url = "https://gamma-api.polymarket.com/events?limit=30&active=true&closed=false"
    
    signals = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for event in data:
            title = event.get('title', '未知事件')
            markets = event.get('markets', [])
            if not markets: continue
            
            m = markets[0]
            raw_prices = m.get('outcomePrices')
            odds = 0.0
            
            try:
                # 处理多种价格格式
                if isinstance(raw_prices, list) and len(raw_prices) > 0:
                    odds = float(raw_prices[0])
                elif isinstance(raw_prices, str):
                    parsed = json.loads(raw_prices)
                    odds = float(parsed[0])
                
                # 校准：API 有时返回 0.54，有时返回 54.0
                if 0 < odds <= 1.0:
                    odds = odds * 100
            except:
                odds = 0.0
            
            slug = event.get('slug', '')
            link = f"https://polymarket.com/event/{slug}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": round(odds, 1),
                "link": link,
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 核心逻辑：按胜率从高到低排序
        signals.sort(key=lambda x: x['odds'], reverse=True)
        print(f"✅ 成功抓取 {len(signals)} 条信号")
        
    except Exception as e:
        print(f"❌ 运行异常: {e}")
        if not signals: return

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_polymarket_data()
