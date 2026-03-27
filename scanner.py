import requests
import json
import os

def fetch_polymarket_data():
    print("🚀 开始扫描 Polymarket 高胜率市场...")
    url = "https://gamma-api.polymarket.com/events?limit=40&active=true&closed=false"
    
    signals = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for event in data:
            title = event.get('title', '未知预测')
            markets = event.get('markets', [])
            if not markets: continue
            
            m = markets[0]
            prices = m.get('outcomePrices')
            odds = 0.0
            
            try:
                # 解析价格并转换为百分比胜率
                if isinstance(prices, list) and len(prices) > 0:
                    odds = float(prices[0])
                elif isinstance(prices, str):
                    odds = float(json.loads(prices)[0])
                
                # 标准化处理 (0.75 -> 75.0)
                if 0 < odds <= 1.0:
                    odds = odds * 100
            except:
                continue
            
            slug = event.get('slug', '')
            link = f"https://polymarket.com/event/{slug}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": round(odds, 1),
                "link": link,
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 核心：高胜率优先排序
        signals.sort(key=lambda x: x['odds'], reverse=True)
        print(f"✅ 成功获取 {len(signals)} 条数据")
        
    except Exception as e:
        print(f"⚠️ 扫描出错: {e}")
        return

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_polymarket_data()
