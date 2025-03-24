# init_pivots.py
import json
import os
from datetime import datetime, timedelta
import pytz
import re

# Đường dẫn đến file lưu trữ các pivot ban đầu
INIT_PIVOTS_FILE = "data/initial_pivots.json"

def save_initial_pivots(pivots):
    """Lưu danh sách pivot ban đầu vào file"""
    try:
        # Đảm bảo thư mục data tồn tại
        if not os.path.exists("data"):
            os.makedirs("data")
            
        with open(INIT_PIVOTS_FILE, "w", encoding="utf-8") as f:
            json.dump(pivots, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Lỗi khi lưu pivot ban đầu: {str(e)}")
        return False

def load_initial_pivots():
    """Đọc danh sách pivot ban đầu từ file"""
    try:
        if os.path.exists(INIT_PIVOTS_FILE):
            with open(INIT_PIVOTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Lỗi khi đọc pivot ban đầu: {str(e)}")
        return []

def parse_date(date_str):
    """
    Phân tích chuỗi ngày tháng ở các định dạng khác nhau
    Hỗ trợ:
    - YYYY-MM-DD (2025-03-23)
    - DD-MM-YYYY (23-03-2025)
    """
    try:
        # Kiểm tra các định dạng ngày
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):  # YYYY-MM-DD
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        elif re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):  # DD-MM-YYYY
            return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
        else:
            # Định dạng không được hỗ trợ, sử dụng ngày hiện tại
            return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%m-%d")
    except Exception:
        # Nếu có lỗi, sử dụng ngày hiện tại
        return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%m-%d")

def parse_pivot_input(pivot_text):
    """
    Phân tích cú pháp đầu vào để tạo pivot
    Định dạng: 
        <loại>:<giá>:<thời_gian> - chỉ giờ:phút, sử dụng ngày hiện tại
        <loại>:<giá>:<ngày>:<thời_gian> - ngày giờ đầy đủ
        
    Hỗ trợ hai định dạng ngày:
        - YYYY-MM-DD (2025-03-23)
        - DD-MM-YYYY (23-03-2025)
        
    Ví dụ: 
        LL:79894:00:30  => sử dụng ngày hiện tại
        LL:79894:2025-03-23:00:30  => YYYY-MM-DD
        LL:79894:23-03-2025:00:30  => DD-MM-YYYY
    """
    try:
        print(f"DEBUG - Parsing input: {pivot_text}")  # In ra console
        
        parts = pivot_text.strip().split(":")
        print(f"DEBUG - Parts: {parts}")
        
        
        # Kiểm tra định dạng đầu vào
        if len(parts) < 3:
            return None
            
        pivot_type = parts[0].upper()  # LL, LH, HL, HH
        price = float(parts[1])
        
        # Lấy ngày hiện tại theo múi giờ Việt Nam
        now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        
        # Kiểm tra xem có phải định dạng đầy đủ ngày giờ không
        date_pattern1 = re.compile(r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
        date_pattern2 = re.compile(r'^\d{2}-\d{2}-\d{4}$')  # DD-MM-YYYY
        
        if len(parts) >= 4 and (date_pattern1.match(parts[2]) or date_pattern2.match(parts[2])):
            # Định dạng có ngày và giờ: <loại>:<giá>:<ngày>:<giờ>
            vn_date = parse_date(parts[2])  # Chuyển đổi sang YYYY-MM-DD
            time_parts = parts[3:]
            
            # Xử lý thời gian
            if len(time_parts) == 1:
                # Định dạng HH:MM
                time_str = time_parts[0]
            else:
                # Định dạng H:M (ghép lại các phần thời gian)
                time_str = ":".join(time_parts)
                
        else:
            # Định dạng chỉ có giờ: <loại>:<giá>:<giờ>
            vn_date = now.strftime("%Y-%m-%d")
            time_parts = parts[2:]
            
            # Xử lý thời gian
            if len(time_parts) == 1:
                # Định dạng HH:MM
                time_str = time_parts[0]
            else:
                # Định dạng H:M (ghép lại các phần thời gian)
                time_str = ":".join(time_parts)
        
        # Chuẩn hóa định dạng thời gian
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_formatted = time_obj.strftime("%H:%M")
        
        # Xác định direction dựa vào loại pivot
        if pivot_type in ["HH", "LH"]:
            direction = "high"
        else:  # LL, HL
            direction = "low"
            
        # Tạo đối tượng pivot
        return {
            "type": pivot_type,
            "price": price,
            "vn_time": time_formatted,
            "vn_date": vn_date,
            "direction": direction,
            "confirmed": True
        }
        
    except Exception as e:
        print(f"Lỗi khi phân tích pivot: {str(e)}")
        return None
