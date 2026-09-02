import os
import json
import time
import requests

API_KEY = os.getenv("GEMINI_API_KEY")
SITE_TYPE = os.getenv("SITE_TYPE", "demong")

# 1. 定义不同赛道的种子关键词分类，确保 AI 生成的内容不重复
KEYWORD_SEEDS = {
    "demong": [
        "con rắn", "tiền bạc", "người yêu cũ", "rụng răng", "nước lũ", "lửa cháy", 
        "mèo đen", "chó cắn", "bay trên trời", "người chết", "đám cưới", "bắt cá",
        "trúng số", "xe tai nạn", "gãy tay", "khóc lóc", "bị đuổi bắt", "mất đồ"
    ],
    "xingzuo": [
        "Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ",
        "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"
    ],
    "fengshui": [
        "xem ngày tốt mua xe", "ngày tốt khai trương", "ngày tốt chuyển nhà",
        "hướng nhà hợp tuổi", "màu sắc may mắn", "phong thủy phòng ngủ", "phong thủy bàn làm việc"
    ]
}

def call_gemini_for_json(seed_word):
    """调用 Gemini 批量生成标准 JSON 格式数据"""
    if not API_KEY:
        print("未检测到 GEMINI_API_KEY！")
        return []

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    prompt = f"""
    Bạn là một chuyên gia về {SITE_TYPE}. Hãy tạo 20 mục giải mã/tử vi/phong thủy khác nhau liên quan đến từ khóa: "{seed_word}".
    Tất cả bằng tiếng Việt.
    Yêu cầu trả về BẮT BUỘC là một MẢNG JSON thuần (Pure JSON Array), KHÔNG dùng Markdown block, KHÔNG ghi chú thích.

    Cấu trúc từng Element trong Array:
    {{
        "title": "Tiêu đề ngắn gọn (ví dụ: Mơ thấy {seed_word} bò vào nhà)",
        "category": "Giải mã giấc mơ",
        "meaning": "Đoạn văn giải thích chi tiết điềm báo từ 2-3 câu...",
        "numbers": "2 con số may mắn cách nhau bởi dấu phẩy, ví dụ: 32, 72"
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"} # 强制要求返回 JSON
    }
    
    try:
        res = requests.post(url, json=payload, timeout=40)
        res_json = res.json()
        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
        return json.loads(raw_text)
    except Exception as e:
        print(f"处理关键词 [{seed_word}] 时失败: {e}")
        return []

# 2. 读取已有的 data.json 数据
json_file = "data.json"
existing_data = []
if os.path.exists(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except:
        existing_data = []

# 获取目前最大的 ID
start_id = max([item.get("id", 0) for item in existing_data], default=0) + 1

# 3. 循环种子词，批量扩充数据
seeds = KEYWORD_SEEDS.get(SITE_TYPE, KEYWORD_SEEDS["demong"])
new_added_count = 0

print(f"开始使用 AI 为 [{SITE_TYPE}] 赛道批量生成词库...")

for seed in seeds:
    print(f"正在生成与 [{seed}] 相关的 20 条词条...")
    items = call_gemini_for_json(seed)
    
    for item in items:
        # 生成标准的 slug 路径名
        clean_title = item.get("title", "").lower()
        slug = f"post-{start_id}"
        
        item["id"] = start_id
        item["slug"] = slug
        existing_data.append(item)
        
        start_id += 1
        new_added_count += 1
    
    # 避免请求过于频繁触发 API 速率限制
    time.sleep(2)

# 4. 覆盖写入 data.json
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=2)

print(f"批量生成完成！本次新增 {new_added_count} 条，全站总数据量达到 {len(existing_data)} 条。")
