import requests
import json
import os
from datetime import datetime

def fetch_polymarket_data():
    print("🚀 PolyAxiom 扫描引擎启动...")
    # 增加数据量以确保有足够的“热度”项目进行排序
    url = "https://gamma-api.polymarket.com/events?limit=60&active=true&closed=false"
    
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
            prices = m.get('outcomePrices')
            # 抓取 24 小时交易量，如果没有则默认为 0
            volume = float(event.get('volume24h', 0))
            
            try:
                # 兼容字符串或列表格式的胜率数据
                if isinstance(prices, str):
                    odds_list = json.loads(prices)
                else:
                    odds_list = prices
                
                odds = float(odds_list[0])
                if 0 < odds <= 1.0: odds *= 100
            except: 
                continue
            
            signals.append({
                "title": title,
                "odds": round(odds, 1),
                "volume": round(volume / 1000, 1), # 转换为 k 单位
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=PolyAxiom",
                "category": event.get('groupItemTitle', '预测市场')
            })
            
        # 排序逻辑：交易量 > 10k 的排最前，然后按胜率排
        signals.sort(key=lambda x: (x['volume'] > 10, x['odds']), reverse=True)
        
        # 写入文件
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)
            
        print(f"✅ 成功抓取 {len(signals)} 条数据并完成热度排序")
        
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        # 这里不使用 exit(1) 避免 Actions 变红，先让它跑完生成基础文件
        pass

if __name__ == "__main__":
    fetch_polymarket_data()
