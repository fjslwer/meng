import os
import json
import time
import requests

API_KEY = os.getenv("GEMINI_API_KEY")
SITE_TYPE = os.getenv("SITE_TYPE", "demong")

# 大幅扩充后的越南语长尾种子词库
KEYWORD_SEEDS = {
    "demong": [
        # 动物类
        "con rắn", "con chó", "con mèo", "con cá", "con hổ", "con rồng", "con chim", "con trâu", "con lợn", "con gà",
        # 自然与人体
        "rụng răng", "gãy tay", "nước lũ", "lửa cháy", "mưa to", "mặt trời", "biển cả", "sông sâu", "mất tóc",
        # 物品与财富
        "tiền bạc", "nhặt được vàng", "trúng số", "mất xe", "mất điện thoại", "nhà cũ", "mua nhà mới", "quần áo mới",
        # 情感与生活
        "người yêu cũ", "đám cưới", "người chết", "cãi nhau", "bị đuổi bắt", "khóc lóc", "đi du lịch", "sinh con"
    ],
    "xingzuo": [
        "Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ",
        "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"
    ],
    "fengshui": [
        "xem ngày tốt mua xe", "ngày tốt khai trương", "ngày tốt chuyển nhà", "ngày tốt cưới hỏi",
        "hướng nhà hợp tuổi", "màu sắc may mắn 2026", "phong thủy phòng ngủ", "phong thủy bàn làm việc", "cây phong thủy"
    ]
}

def call_gemini_for_json(seed_word):
    if not API_KEY:
        return []

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # 修改 Prompt：要求 AI 针对每个种子词深入扩展 15 个细分长尾词，并且要求更详尽的解说
    prompt = f"""
    Bạn là chuyên gia tâm linh/phong thủy. Hãy tạo 15 mục giải mã/tử vi chi tiết liên quan đến từ khóa: "{seed_word}".
    Tất cả bằng tiếng Việt.
    Yêu cầu trả về BẮT BUỘC là một MẢNG JSON thuần (Pure JSON Array), KHÔNG Markdown, KHÔNG chú thích.

    Cấu trúc từng Element:
    {{
        "title": "Tiêu đề cụ thể (Ví dụ: Mơ thấy {seed_word} rượt đuổi mình / Mơ thấy {seed_word} màu vàng)",
        "category": "Giải mã giấc mơ",
        "meaning": "Viết đoạn văn giải thích rất chi tiết từ 4-6 câu bao gồm: Điềm báo tốt hay xấu, ý nghĩa tâm linh, lời khuyên cho công việc/tình cảm trong thời gian tới.",
        "numbers": "3 con số may mắn (Ví dụ: 32, 72, 89)"
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
    try:
        res = requests.post(url, json=payload, timeout=40)
        res_json = res.json()
        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
        return json.loads(raw_text)
    except Exception as e:
        print(f"处理关键词 [{seed_word}] 失败: {e}")
        return []

# 读取并写入逻辑
json_file = "data.json"
existing_data = []
if os.path.exists(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except:
        existing_data = []

# 建立已有 title 集合，防止重复写入
existing_titles = set(item.get("title") for item in existing_data)
start_id = max([item.get("id", 0) for item in existing_data], default=0) + 1

seeds = KEYWORD_SEEDS.get(SITE_TYPE, KEYWORD_SEEDS["demong"])
print(f"开始扩充 [{SITE_TYPE}] 词库...")

for seed in seeds:
    print(f"正在生成: [{seed}] ...")
    items = call_gemini_for_json(seed)
    
    for item in items:
        if item.get("title") not in existing_titles:
            item["id"] = start_id
            item["slug"] = f"bai-viet-{start_id}"
            existing_data.append(item)
            existing_titles.add(item.get("title"))
            start_id += 1
            
    time.sleep(1.5)

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=2)

print(f"词库扩充完成，当前全站共有 {len(existing_data)} 条数据！")
