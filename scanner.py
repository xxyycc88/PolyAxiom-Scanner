import requests
import json
import os

def fetch_polymarket_data():
    print("🔍 PolyAxiom 数据引擎启动...")
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
                # 处理 Polymarket 多样化的价格字段
                if isinstance(raw_prices, list) and len(raw_prices) > 0:
                    odds = float(raw_prices[0])
                elif isinstance(raw_prices, str):
                    odds = float(json.loads(raw_prices)[0])
                
                # 校准：如果 API 返回 0.545 格式，转换为 54.5%
                if 0 < odds <= 1.0:
                    odds = odds * 100
                elif odds > 100: # 极端异常处理
                    odds = 0.0
            except:
                odds = 0.0
            
            slug = event.get('slug', '')
            # 自动注入你的推荐后缀
            link = f"https://polymarket.com/event/{slug}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": round(odds, 2), # 保留两位小数更显专业
                "link": link,
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 排序：高胜率优先
        signals.sort(key=lambda x: x['odds'], reverse=True)
        print(f"✅ 同步完成，获取到 {len(signals)} 条信号")
        
    except Exception as e:
        print(f"❌ 运行报错: {e}")
        return

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_polymarket_data()
