import os
import json
import requests
from datetime import datetime

today_str = datetime.now().strftime("%d/%m/%Y")
today_sitemap_date = datetime.now().strftime("%Y-%m-%d")

SITE_TYPE = os.getenv("SITE_TYPE", "demong")
DOMAIN = os.getenv("SITE_DOMAIN", "https://somo24h.com")
API_KEY = os.getenv("GEMINI_API_KEY")

print(f"[{datetime.now()}] 正在为站点 ({DOMAIN}) 执行更新，赛道类型: [{SITE_TYPE}]...")

def generate_ai_content(prompt):
    if not API_KEY:
        return f"Tử vi ngày {today_str}: Cát lành, suôn sẻ, may mắn tài lộc."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"API 请求失败: {e}")
        return f"Tử vi ngày {today_str}: Chúc bạn một ngày tràn đầy năng lượng."

if SITE_TYPE == "xingzuo":
    prompt = f"Viết một bản tin tử vi ngắn gọn cho 12 cung hoàng đạo ngày {today_str} bằng tiếng Việt."
    ai_text = generate_ai_content(prompt)
    new_item = {
        "id": int(datetime.now().timestamp()),
        "title": f"✨ Tử vi 12 cung hoàng đạo ngày {today_str}",
        "category": "Tử vi hàng ngày",
        "meaning": ai_text,
        "numbers": "12, 08, 99"
    }
elif SITE_TYPE == "fengshui":
    prompt = f"Viết xem ngày tốt xấu, giờ hoàng đạo ngày {today_str} theo phong thủy bằng tiếng Việt."
    ai_text = generate_ai_content(prompt)
    new_item = {
        "id": int(datetime.now().timestamp()),
        "title": f"⛩️ Xem ngày tốt xấu & Giờ hoàng đạo ngày {today_str}",
        "category": "Phong thủy chọn ngày",
        "meaning": ai_text,
        "numbers": "01, 06, 68"
    }
else:
    prompt = f"Viết giải mã một giấc mơ phổ biến và cho con số may mắn ngày {today_str} bằng tiếng Việt."
    ai_text = generate_ai_content(prompt)
    new_item = {
        "id": int(datetime.now().timestamp()),
        "title": f"🔮 Giải mã giấc mơ hot ngày {today_str}",
        "category": "Giải mã giấc mơ",
        "meaning": ai_text,
        "numbers": f"{datetime.now().day}, {datetime.now().month}, 88"
    }

json_file = "data.json"
data = []
if os.path.exists(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

data.insert(0, new_item)

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{DOMAIN}/</loc>
    <lastmod>{today_sitemap_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_content)

print("数据及 sitemap.xml 刷写入库完成。")
