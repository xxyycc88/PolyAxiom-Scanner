import requests
import json
import os

def fetch_polymarket_data():
    print("🔍 正在抓取 Polymarket 实时预测数据...")
    url = "https://gamma-api.polymarket.com/events?limit=15&active=true&closed=false"
    
    signals = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for event in data:
            title = event.get('title', '未知事件')
            markets = event.get('markets', [{}])
            if not markets: continue
            
            # 改进的赔率提取逻辑：确保能拿到数字
            outcome_prices = markets[0].get('outcomePrices')
            try:
                # 尝试取第一个选项的价格，转为浮点数
                if isinstance(outcome_prices, list) and len(outcome_prices) > 0:
                    odds = float(outcome_prices[0])
                elif isinstance(outcome_prices, str):
                    # 如果是字符串形式的列表 "[0.5, 0.5]"，尝试解析
                    prices = json.loads(outcome_prices)
                    odds = float(prices[0])
                else:
                    odds = 0.5
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
        print(f"✅ 成功抓取 {len(signals)} 条真实信号")
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        if not signals:
            signals = [{"title": "信号同步中...", "odds": 0.0, "link": "#", "category": "System"}]

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=4)
    print("🚀 data.json 已更新")

if __name__ == "__main__":
    fetch_polymarket_data()
