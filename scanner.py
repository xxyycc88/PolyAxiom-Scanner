import os
import requests
from supabase import create_client, Client

# 配置信息
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") # 必须是 GitHub Secrets 里的 service_role key

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ 错误: 环境变量配置缺失")
    exit(1)

# 初始化上帝模式客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_polymarket_signals():
    """抓取逻辑，你可以根据需要修改这里的内容"""
    print("🔍 正在扫描全球预测市场...")
    return [
        {
            "title": "NBA: Lakers vs Warriors - Market Analysis",
            "ai_summary": "AI 监测到大额资金流入，当前赔率存在套利空间。",
            "referral_link": "https://polymarket.com/event/lakers-vs-warriors?referral=XXYY"
        },
        {
            "title": "Fed Interest Rate Decision (May 2026)",
            "ai_summary": "预测市场暗示维持利率不变的概率为 72%。",
            "referral_link": "https://polymarket.com/event/fed-may-2026?referral=XXYY"
        }
    ]

def save_to_supabase(signals):
    for signal in signals:
        try:
            # 使用 upsert：根据 title 判断，存在则更新，不存在则插入
            # 这样 GitHub Actions 永远不会报 23505 错误
            supabase.table("alpha_signals").upsert(
                signal, on_conflict="title"
            ).execute()
            print(f"✅ 信号同步成功: {signal['title']}")
        except Exception as e:
            print(f"❌ 运行异常: {str(e)}")

if __name__ == "__main__":
    found_signals = get_polymarket_signals()
    if found_signals:
        save_to_supabase(found_signals)
