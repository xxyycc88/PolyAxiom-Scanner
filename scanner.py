import os
import requests
from supabase import create_client

# 1. 配置钥匙 (从 GitHub Secrets 读取)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
ds_api_key = os.environ.get("DEEPSEEK_API_KEY")

supabase = create_client(url, key)

def analyze_with_ai(title):
    """调用 DeepSeek 进行中文解析"""
    try:
        headers = {"Authorization": f"Bearer {ds_api_key}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个专业的预测市场分析师。"},
                {"role": "user", "content": f"请用一句话简要分析这个预测市场的中文背景：{title}"}
            ]
        }
        res = requests.post("https://api.deepseek.com/chat/completions", json=data, headers=headers, timeout=20)
        return res.json()['choices'][0]['message']['content']
    except:
        return "点击查看详情分析..."

def run_scanner():
    print("开始扫描 Polymarket...")
    # 获取最热门的 20 个市场
    response = requests.get("https://gamma-api.polymarket.com/events?active=true&limit=20")
    markets = response.json()
    
    for m in markets:
        title = m.get('title')
        slug = m.get('slug')
        
        # 让 AI 生成中文简评
        ai_msg = analyze_with_ai(title)
        
        # 准备存入数据库的数据
        row = {
            "title": title,
            "odds": 0.5, # 基础版本先占位，后续可接入实时赔率
            "ai_summary": ai_msg,
            "referral_link": f"https://polymarket.com/event/{slug}?r=PolyAxiom"
        }
        
        # 存入 Supabase (如果标题重复则更新)
        supabase.table("alpha_signals").upsert(row, on_conflict="title").execute()
        print(f"✅ 已同步: {title}")

if __name__ == "__main__":
    run_scanner()
