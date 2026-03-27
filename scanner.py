import requests
import json
import os

def fetch_polymarket_data():
    print("🔍 开始同步 PolyAxiom 核心数据...")
    # 增加 limit 到 30，确保有足够的高质量信号
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
            
            # 核心改进：多路径价格抓取逻辑
            m = markets[0]
            raw_prices = m.get('outcomePrices')
            odds = 0.0
            
            try:
                # 路径 1: 标准列表格式 [0.6, 0.4]
                if isinstance(raw_prices, list) and len(raw_prices) > 0:
                    odds = float(raw_prices[0])
                # 路径 2: 字符串化列表 "[0.6, 0.4]"
                elif isinstance(raw_prices, str):
                    parsed = json.loads(raw_prices)
                    odds = float(parsed[0])
                
                # 路径 3: 如果还是 0，尝试读取最新成交价 (Best Bid/Ask 的中点)
                if odds == 0:
                    # 有些新市场 API 还没刷出 outcomePrices，给个默认参考值
                    odds = float(m.get('lastTradePrice', 0.5))
            except:
                odds = 0.5 # 兜底值
            
            slug = event.get('slug', '')
            # 确保邀请码永远存在
            link = f"https://polymarket.com/event/{slug}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": odds,
                "link": link,
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 按照胜率从高到低排序，让你的页面看起来更专业
        signals.sort(key=lambda x: x['odds'], reverse=True)
        print(f"✅ 成功同步 {len(signals)} 条信号")
        
    except Exception as e:
        print(f"❌ 抓取异常: {e}")
        # 即使报错也要保留老数据或展示同步中，绝对不让 data.json 消失
        if not signals:
            return 

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=4)
    print("🚀 静态数据已写入仓库，准备上线")

if __name__ == "__main__":
    fetch_polymarket_data()
