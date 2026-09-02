import os
import json
import requests
from datetime import datetime

today_str = datetime.now().strftime("%d/%m/%Y")
today_sitemap_date = datetime.now().strftime("%Y-%m-%d")

SITE_TYPE = os.getenv("SITE_TYPE", "demong")
DOMAIN = os.getenv("SITE_DOMAIN", "https://somo24h.com")

json_file = "data.json"
data = []
if os.path.exists(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

# HTML 模版强化：增加结构化排版
def get_html_template(page_title, content_body, meta_desc):
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - Tra Cứu Phong Thủy & Tử Vi 2026</title>
    <meta name="description" content="{meta_desc[:150]}">
    <style>
        :root {{ --primary: #4a154b; --bg: #f9f6fa; --accent: #f4c430; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); margin: 0; padding: 0; color: #2d3436; line-height: 1.6; }}
        header {{ background: var(--primary); color: var(--accent); padding: 15px; text-align: center; border-bottom: 3px solid var(--accent); }}
        header a {{ color: var(--accent); text-decoration: none; font-weight: bold; font-size: 1.2rem; }}
        .container {{ max-width: 650px; margin: 15px auto; padding: 0 12px; }}
        .card {{ background: #fff; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
        h1 {{ color: var(--primary); font-size: 1.4rem; margin-top: 0; border-bottom: 2px solid #f1f1f1; padding-bottom: 8px; }}
        h2 {{ color: var(--primary); font-size: 1.1rem; margin-top: 20px; }}
        .lucky-box {{ background: #fff8e1; border: 1px solid #ffe082; color: #b78103; padding: 12px; border-radius: 8px; font-weight: bold; text-align: center; font-size: 1.05rem; margin: 15px 0; }}
        .dos-donts {{ display: flex; gap: 10px; margin: 15px 0; }}
        .do-box {{ flex: 1; background: #e8f5e9; padding: 10px; border-radius: 6px; font-size: 0.85rem; }}
        .dont-box {{ flex: 1; background: #ffebee; padding: 10px; border-radius: 6px; font-size: 0.85rem; }}
        .related-list a {{ display: block; padding: 10px 0; color: var(--primary); text-decoration: none; border-bottom: 1px solid #f0f0f0; font-size: 0.95rem; }}
        .ad-box {{ background: #f8f9fa; padding: 12px; text-align: center; font-size: 0.8rem; color: #a1a1a1; border: 1px dashed #ccc; margin: 15px 0; border-radius: 6px; }}
        footer {{ text-align: center; padding: 25px; font-size: 0.8rem; color: #888; }}
    </style>
</head>
<body>
<header><a href="/">🔮 GIẢI MÃ & TỬ VI 247</a></header>
<div class="container">
    <div class="ad-box">[ AdSense Banner Responsive Header ]</div>
    {content_body}
    <div class="ad-box">[ AdSense In-Article Slot ]</div>
</div>
<footer>© 2026 {DOMAIN}. Chúc bạn may mắn và hanh thông.</footer>
</body>
</html>"""

os.makedirs("detail", exist_ok=True)
sitemap_urls = [f"{DOMAIN}/"]

# 循环生成单页
for idx, item in enumerate(data):
    slug = item.get("slug", f"bai-viet-{item['id']}")
    file_path = f"detail/{slug}.html"
    page_url = f"{DOMAIN}/detail/{slug}.html"
    sitemap_urls.append(page_url)
    
    # 建立 8 条相关文章内链网络
    related_html = "<div class='card'><h2>🔍 Các điềm báo liên quan khác:</h2><div class='related-list'>"
    for r_item in data[max(0, idx-4):idx] + data[idx+1:idx+5]:
        r_slug = r_item.get("slug", f"bai-viet-{r_item['id']}")
        related_html += f"<a href='/detail/{r_slug}.html'>👉 {r_item['title']}</a>"
    related_html += "</div></div>"

    # 单页内容丰富化排版
    body_content = f"""
    <article class="card">
        <h1>{item['title']}</h1>
        <p><strong>Danh mục:</strong> {item.get('category', 'Giải mã giấc mơ')}</p>
        
        <h2>1. Ý nghĩa & Điềm báo chi tiết</h2>
        <p>{item['meaning']}</p>
        
        <div class="lucky-box">🎲 Con số may mắn liên quan: {item['numbers']}</div>
        
        <h2>2. Lời khuyên nên làm & nên tránh</h2>
        <div class="dos-donts">
            <div class="do-box"><strong>Nên làm:</strong> Giữ tinh thần lạc quan, chủ động nắm bắt cơ hội kinh doanh.</div>
            <div class="dont-box"><strong>Nên tránh:</strong> Hạn chế đầu tư mạo hiểm hoặc gây tranh cãi trong ngày.</div>
        </div>

        <h2>3. Câu hỏi thường gặp (FAQ)</h2>
        <p><strong>Điềm báo này kéo dài bao lâu?</strong> Thông thường các điềm báo tâm linh sẽ ứng nghiệm trong vòng 3到7 ngày tới.</p>
    </article>
    {related_html}
    """
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(get_html_template(item['title'], body_content, item['meaning']))

# 首页渲染：列出最新 50 条
home_list_html = "<div class='card'><h1>Top Tra Cứu Hot Nhất 2026</h1><div class='related-list'>"
for item in data[:50]:
    slug = item.get("slug", f"bai-viet-{item['id']}")
    home_list_html += f"<a href='/detail/{slug}.html'>🔮 {item['title']}</a>"
home_list_html += "</div></div>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(get_html_template("Trang Chủ - Giải Mã Điềm Báo & Tử Vi 2026", home_list_html, "Tra cứu điềm báo, sổ mơ lô đề, tử vi phong thủy chuẩn xác nhất."))

# 生成 Sitemap
xml_entries = "".join([f"<url><loc>{url}</loc><lastmod>{today_sitemap_date}</lastmod></url>" for url in sitemap_urls])
sitemap_xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{xml_entries}</urlset>'

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_xml)

print("SSG 编译完成！所有页面已做丰满化排版优化。")
