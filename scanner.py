import requests
import json
import os
import random

def fetch_polymarket_data():
    print("📡 PolyAxiom 2.0 引擎启动：正在通过 Builder 接口扫描信号...")
    
    # 从 GitHub Secrets 中读取你的 Key (请确保你在 GitHub 设置里存的名字一致)
    api_key = os.getenv('POLY_API_KEY')
    
    # 接口地址保持 Gamma API 以获取 Event 流
    url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false"
    
    headers = {
        "User-Agent": "PolyAxiom-Scanner/2.0",
        "x-api-key": api_key if api_key else "" # 如果还没设置 Key，脚本也能兼容运行
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        data = response.json()
        signals = []

        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets or not title: continue
            
            # 锁定第一个盘口数据
            m = markets[0]
            try:
                prices_raw = m.get('outcomePrices')
                prices = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
                
                # 核心修复 1：过滤无价格数据
                if not prices or len(prices) == 0:
                    continue
                
                odds_val = float(prices[0])
                
                # 核心修复 2：过滤 < 0.5% 的僵尸项目
                if odds_val < 0.005: 
                    continue
                    
                odds = round(odds_val * 100, 1)
            except:
                continue

            # 获取成交额并标记异动
            v_event = float(event.get('volume', 0))
            # 标记逻辑：成交额 > 2k 且胜率 > 5% 视为热门
            is_hot = True if v_event > 2000 and odds > 5 else False

            signals.append({
                "title": title,
                "odds": odds,
                "volume": round(v_event / 1000, 1),
                "is_hot": is_hot,
                # ✅ 统一更新为 Axiomcom 邀请码，保持返佣逻辑一致
                "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=Axiomcom",
                "rand_score": random.uniform(0, 10)
            })

        # 排序：异动项目置顶，其他随机洗牌增加页面多样性
        signals.sort(key=lambda x: (x['is_hot'], x['rand_score']), reverse=True)

        # 写入 data.json (只取前 40 个最优质信号)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(signals[:40], f, ensure_ascii=False, indent=4)
            
        print(f"✅ 扫描完成！已同步 {len(signals[:40])} 个有效信号至 data.json")

    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    fetch_polymarket_data()
