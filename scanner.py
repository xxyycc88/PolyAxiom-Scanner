import requests
import json
import os

def fetch_polymarket_data():
    print("🔍 正在抓取 Polymarket 实时预测数据...")
    # 这里使用的是 Polymarket 的公开 API 节点
    url = "https://gamma-api.polymarket.com/events?limit=10&active=true&closed=false"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        signals = []
        for event in data:
            # 提取标题、赔率（取第一个 market 的价格）
            title = event.get('title', 'Unknown Event')
            markets = event.get('markets', [{}])
            # 简化逻辑：取第一个选项的价格作为 odds
            outcome_prices = markets[0].get('outcomePrices', ['0.5', '0.5'])
            odds = float(outcome_prices[0])
            
            # 拼接 PolyAxiom 专属邀请链接
            slug = event.get('slug', '')
            link = f"https://polymarket.com/event/{slug}?r=PolyAxiom"
            
            signals.append({
                "title": title,
                "odds": odds,
                "link": link,
                "category": event.get('groupItemTitle', 'Market')
            })
        
        # 将结果保存为本地 JSON 文件
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 成功抓取 {len(signals)} 条信号并生成 data.json")
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()
