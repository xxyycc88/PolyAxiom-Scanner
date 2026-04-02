import os
import requests
import json
import random
import time
from decimal import Decimal

# ✅ 核心配置：从 GitHub Secrets 读取你的钥匙
API_KEY = os.getenv('POLY_API_KEY')
API_SECRET = os.getenv('POLY_API_SECRET') # 如果需要签名验证需要用到

# 巨鲸大单阈值 (USDC)
WHALE_THRESHOLD = 5000 

class PolyAxiomScanner:
    def __init__(self):
        self.gamma_api = "https://gamma-api.polymarket.com"
        self.clob_api = "https://clob.polymarket.com"
        self.headers = {
            "User-Agent": "PolyAxiom-Scanner/3.0",
            "x-api-key": API_KEY if API_KEY else ""
        }
        self.signals = []

    def log(self, msg):
        print(f"[📡 PolyAxiom 3.0] {msg}")

    def fetch_active_events(self):
        self.log("正在扫描 Gamma API 获取活跃项目...")
        url = f"{self.gamma_api}/events?limit=80&active=true&closed=false&creator=Axiomcom"
        try:
            res = requests.get(url, headers=self.headers, timeout=15)
            return res.json()
        except Exception as e:
            self.log(f"Gamma API 抓取失败: {e}")
            return []

    def check_whale_activity(self, condition_id):
        """
        🚀 Builder 专属：利用 CLOB 接口检查指定盘口的巨鲸大单
        """
        if not API_KEY: return False # 无 Key 不跑 Builder 逻辑

        url = f"{self.clob_api}/trades/{condition_id}"
        try:
            # Builder Key 可以在这里增加频率或深度
            res = requests.get(url, headers=self.headers, timeout=10)
            trades = res.json()
            if not trades or not isinstance(trades, list): return False

            # 只检查最近的 20 笔成交
            recent_trades = trades[:20]
            for trade in recent_trades:
                size = Decimal(trade.get('size', '0'))
                price = Decimal(trade.get('price', '0'))
                # 计算成交金额 (USDC)
                notional = size * price
                
                if notional >= WHALE_THRESHOLD:
                    self.log(f"⚠️ 发现巨鲸！盘口 {condition_id} 成交额: ${notional:.2f}")
                    return True # 发现一笔即视为有巨鲸活动

            return False
        except:
            return False

    def run(self):
        start_time = time.time()
        events = self.fetch_active_events()
        if not events: return

        processed_count = 0
        for event in events:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets or not title: continue
            
            m = markets[0]
            condition_id = m.get('conditionId') # 核心：用于 CLOB 抓取
            if not condition_id: continue

            try:
                prices_raw = m.get('outcomePrices')
                prices = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
                if not prices or len(prices) == 0: continue
                
                odds_val = float(prices[0])
                if odds_val < 0.005 or odds_val > 0.995: continue # 过滤无效盘口
                odds = round(odds_val * 100, 1)

                v_event = float(event.get('volume', 0))
                is_hot = True if v_event > 5000 and odds > 5 else False

                # 🚀 巨鲸大单追踪逻辑 (只对有热度的项目进行深度扫描，节省配额)
                is_whale = False
                if is_hot or odds > 50:
                    is_whale = self.check_whale_activity(condition_id)
                    # 避免对 CLOB 接口造成过大压力
                    if API_KEY: time.sleep(0.5) 

                self.signals.append({
                    "title": title,
                    "odds": odds,
                    "volume": round(v_event / 1000, 1),
                    "is_hot": is_hot,
                    "is_whale": is_whale, # ✅ 新增巨鲸标记
                    # 统一邀请码
                    "link": f"https://polymarket.com/event/{event.get('slug', '')}?r=Axiomcom",
                    "rand_score": random.uniform(0, 10)
                })
                processed_count += 1

            except: continue

        # 排序：巨鲸项目排最前，其次热门，其次随机洗牌
        self.signals.sort(key=lambda x: (x['is_whale'], x['is_hot'], x['rand_score']), reverse=True)

        # 写入 data.json
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(self.signals[:40], f, ensure_ascii=False, indent=4)
            
        end_time = time.time()
        self.log(f"✅ 扫描完成！处理了 {processed_count} 个项目，同步了 {len(self.signals[:40])} 个 Alpha 信号。耗时: {end_time - start_time:.1f}s")

if __name__ == "__main__":
    scanner = PolyAxiomScanner()
    scanner.run()
