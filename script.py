import os
import json
import requests
from datetime import datetime

# 1. 配置参数
today_str = datetime.now().strftime("%d/%m/%Y")
today_sitemap_date = datetime.now().strftime("%Y-%m-%d")

SITE_TYPE = os.getenv("SITE_TYPE", "demong")
DOMAIN = os.getenv("SITE_DOMAIN", "https://somo24h.com")
API_KEY = os.getenv("GEMINI_API_KEY")

print(f"开始编译 SSG 站点: [{DOMAIN}] (赛道: {SITE_TYPE})...")

# 2. 自动生成每日 AI 新内容
def generate_ai_content(prompt):
    if not API_KEY:
        return "Nội dung dự báo hàng ngày đang được cập nhật."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, json=payload, timeout=30)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"API 请求失败: {e}")
        return "Nội dung đang cập nhật."

# 根据赛道生成新词条
timestamp_id = int(datetime.now().timestamp())
if SITE_TYPE == "xingzuo":
    title = f"Tử vi 12 cung hoàng đạo ngày {today_str}"
    meaning = generate_ai_content(f"Viết tử vi 12 cung hoàng đạo ngày {today_str} bằng tiếng Việt.")
    category = "Tu Vi"
elif SITE_TYPE == "fengshui":
    title = f"Xem ngày tốt xấu & Giờ hoàng đạo ngày {today_str}"
    meaning = generate_ai_content(f"Viết xem ngày tốt xấu phong thủy ngày {today_str} bằng tiếng Việt.")
    category = "Phong Thuy"
else:
    title = f"Mơ thấy điềm báo may mắn ngày {today_str}"
    meaning = generate_ai_content(f"Viết giải mã giấc mơ và số may mắn ngày {today_str} bằng tiếng Việt.")
    category = "Giai Ma Giac Mo"

new_item = {
    "id": timestamp_id,
    "slug": f"bai-viet-{timestamp_id}",
    "title": title,
    "category": category,
    "meaning": meaning,
    "numbers": f"{datetime.now().day}, {datetime.now().month}, 88"
}

# 3. 读取本地 JSON 数据库
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

# 4. SSG 核心：HTML 模板生成器
def get_html_template(page_title, content_body, meta_desc):
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - Tra Cứu 2026</title>
    <meta name="description" content="{meta_desc[:150]}">
    <style>
        :root {{ --primary: #4a154b; --bg: #f9f6fa; }}
        body {{ font-family: -apple-system, sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }}
        header {{ background: var(--primary); color: #f4c430; padding: 15px; text-align: center; }}
        header a {{ color: #f4c430; text-decoration: none; font-weight: bold; font-size: 1.2rem; }}
        .container {{ max-width: 600px; margin: 15px auto; padding: 0 12px; }}
        .card {{ background: #fff; border-radius: 8px; padding: 18px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        h1 {{ color: var(--primary); font-size: 1.3rem; margin-top: 0; }}
        .lucky {{ background: #fff8e1; color: #b78103; padding: 6px 12px; border-radius: 20px; font-weight: bold; display: inline-block; margin-top: 10px; }}
        .related a {{ display: block; padding: 8px 0; color: var(--primary); text-decoration: none; border-bottom: 1px solid #eee; }}
        .ad-box {{ background: #f1f1f1; padding: 10px; text-align: center; font-size: 0.8rem; color: #888; margin: 10px 0; border: 1px dashed #ccc; }}
        footer {{ text-align: center; padding: 20px; font-size: 0.8rem; color: #777; }}
    </style>
</head>
<body>
<header><a href="/">{SITE_TYPE.upper()} TRA CỨU 2026</a></header>
<div class="container">
    <div class="ad-box">[ AdSense Banner Slot ]</div>
    {content_body}
    <div class="ad-box">[ AdSense In-Article Slot ]</div>
</div>
<footer>© 2026 {DOMAIN}. All rights reserved.</footer>
</body>
</html>"""

# 5. 生成各个独立的静态 HTML 详情页 (Detail Pages)
os.makedirs("detail", exist_ok=True)
sitemap_urls = [f"{DOMAIN}/"]

for idx, item in enumerate(data):
    slug = item.get("slug", f"post-{item['id']}")
    file_path = f"detail/{slug}.html"
    page_url = f"{DOMAIN}/detail/{slug}.html"
    sitemap_urls.append(page_url)
    
    # 构造交叉内链（推荐其他 5 条数据）
    related_html = "<div class='card classRelated'><h3>Xem thêm giải mã khác:</h3>"
    for r_item in data[max(0, idx-5):idx] + data[idx+1:idx+6]:
        r_slug = r_item.get("slug", f"post-{r_item['id']}")
        related_html += f"<a href='/detail/{r_slug}.html'>🔮 {r_item['title']}</a>"
    related_html += "</div>"

    body_content = f"""
    <article class="card">
        <h1>{item['title']}</h1>
        <p>{item['meaning']}</p>
        <div class="lucky">🎲 Con số may mắn: {item['numbers']}</div>
    </article>
    {related_html}
    """
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(get_html_template(item['title'], body_content, item['meaning']))

# 6. 生成首页 index.html (包含全站最新文章列表入口)
home_list_html = "<div class='card'><h2>Danh sách giải mã mới nhất</h2>"
for item in data[:30]:  # 首页展示最新 30 条链接
    slug = item.get("slug", f"post-{item['id']}")
    home_list_html += f"<div class='related'><a href='/detail/{slug}.html'>👉 {item['title']}</a></div>"
home_list_html += "</div>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(get_html_template("Trang Chủ - Sổ Mơ & Tử Vi 2026", home_list_html, "Tra cứu sổ mơ, tử vi hàng ngày"))

# 7. 自动生成包含所有静态页面的 sitemap.xml
xml_entries = "".join([f"<url><loc>{url}</loc><lastmod>{today_sitemap_date}</lastmod></url>" for url in sitemap_urls])
sitemap_xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{xml_entries}</urlset>'

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_xml)

print(f"SSG 编译完成！共生成 {len(data)} 个独立 HTML 页面及 Sitemap。")
