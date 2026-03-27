import requests
import json
import os

def fetch_polymarket_data():
    print("🔍 PolyAxiom 数据校准启动...")
    url = "https://gamma-api.polymarket.com/events?limit=25&active=true&closed=false"
    
    signals = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for event in data:
            title = event.get('title', '未知事件')
            markets = event.get('markets', [])
            if not markets: continue
            
            # 精准抓取第一个选项的价格
            m = markets[0]
            raw_prices = m.get('outcomePrices')
            odds = 0.5 # 默认值
            
            try:
                if isinstance(raw_prices, list) and len(raw_prices) > 0:
                    odds = float(raw_prices[0])
                elif isinstance(raw_prices, str):
                    prices_list = json.loads(raw_prices)
                    odds = float(prices_list[0])
                
                # 核心校准：Polymarket API 有时返回的是 0-1 之间的浮点数
                # 如果 odds 已经是百分比形式（例如 54.5），保持不变；
                # 如果是 0.545 形式，前端会乘以 100。
                if odds > 1.0: 
                    odds = odds / 100.0
            except:
                odds = 0.5
            
            slug = event.get('slug', '')
            link = f"https://polymarket.com/event/{slug}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": odds,
                "link": link,
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 排序：让胜率最高的排在前面
        signals.sort(key=lambda x: x['odds'], reverse=True)
        print(f"✅ 成功获取 {len(signals)} 条真实赔率信号")
        
    except Exception as e:
        print(f"❌ 运行异常: {e}")
        if not signals: return

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=4)
    print("🚀 data.json 已校准完毕")

if __name__ == "__main__":
    fetch_polymarket_data()
