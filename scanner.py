import requests
import json
import os

def fetch_polymarket_data():
    print("🚀 PolyAxiom 增强型引擎启动...")
    # 增加采样范围到 100，确保能抓到更多有交易量的数据
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"
    
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
            # 策略升级：优先取24h量，为0则取总成交量，再没有就取该Market的成交量
            v24 = float(event.get('volume24h', 0))
            v_event = float(event.get('volume', 0))
            v_market = float(m.get('volume', 0))
            
            # 选一个最大的不为0的数字
            final_vol = max(v24, v_event, v_market)
            
            try:
                prices = m.get('outcomePrices')
                odds_list = json.loads(prices) if isinstance(prices, str) else prices
                odds = round(float(odds_list[0]) * 100, 1)
            except: continue
            
            # 调低异动门槛：只要波动超过 5% 就触发火焰
            is_hot = False
            if title in old_data:
                change = abs(odds - old_data[title])
                if change >= 5: 
                    is_hot = True

            signals.append({
                "title": title,
                "odds": odds,
                "volume": round(final_vol / 1000, 1), # 转换为 k
                "is_hot": is_hot,
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom",
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 排序权重：异动 > 高交易量 > 高胜率
        signals.sort(key=lambda x: (x['is_hot'], x['volume'] > 10, x['odds']), reverse=True)
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)
        print(f"✅ 更新完成。异动门槛已调低，交易量已补齐。")
        
    except Exception as e:
        print(f"❌ 出错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()
