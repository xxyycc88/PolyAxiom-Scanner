import requests
import json
import os

def fetch_polymarket_data():
    print("🚀 PolyAxiom 终极高胜率引擎启动...")
    # 扩大limit至100，确保过滤噪音后仍有足够多干货
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"
    
    # 1. 加载旧数据用于计算异动 (is_hot)
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
                
                # 【核心过滤】胜率低于 5% 的噪音项目，直接跳过
                if odds < 5: continue
                
            except: continue
            
            # 交易量补全逻辑：24h量=0则取总成交量
            v24 = float(event.get('volume24h', 0))
            v_event = float(event.get('volume', 0))
            final_vol = max(v24, v_event)
            
            # 异动检测：只要波动超过 5% 触发 HOT
            is_hot = False
            if title in old_data:
                change = abs(odds - old_data[title])
                if change >= 5: is_hot = True

            signals.append({
                "title": title,
                "odds": odds,
                "volume": round(final_vol / 1000, 1), # 转换为 k 为单位
                "is_hot": is_hot,
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom",
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 终极排序权重：异动项目 -> 90%以上尊贵项目 -> 胜率
        signals.sort(key=lambda x: (x['is_hot'], x['odds'] >= 90, x['odds']), reverse=True)
        
        # 写入文件，仅保留前 40 条精英信号
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)
        print(f"✅ 更新完成。硬过滤 <5% 项目，异动项目置顶。")
        
    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()
