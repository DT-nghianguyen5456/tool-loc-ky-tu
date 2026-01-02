import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image
import re

# Cấu hình trang
st.set_page_config(page_title="Tool Lọc Code Siêu Tốc", page_icon="⚡")

# --- HÀM XỬ LÝ ẢNH ---
def clean_text(text):
    # Lọc bỏ tất cả ký tự đặc biệt, chỉ giữ chữ và số
    return re.sub(r'[^a-zA-Z0-9]', '', text)

def process_image(image_file):
    # 1. Đọc ảnh
    file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    
    # 2. Xử lý ảnh để tìm ô trắng
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Dùng Threshold đơn giản (Hiệu quả nhất với ô trắng nền tối)
    # Ngưỡng 180: Chỉ lấy màu rất sáng (ô trắng)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    
    # Kỹ thuật quan trọng: "Hàn gắn" các vết đứt gãy để ô code thành 1 khối đặc
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Tìm viền
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = w / float(h)
        area = w * h
        
        # BỘ LỌC CỨNG (Loại bỏ 99% nhiễu):
        # 1. Chiều rộng phải lớn hơn chiều cao (Code nằm ngang)
        # 2. Chiều rộng > 50px (Không lấy rác nhỏ)
        # 3. Diện tích phải đủ lớn
        if w > h and w > 50 and area > 1000:
            valid_boxes.append((x, y, w, h))
            
    # --- SAFETY LOCK (CHỐNG TREO MÁY) ---
    # Nếu tìm thấy quá nhiều ô (do nhiễu), chỉ lấy 25 ô to nhất
    if len(valid_boxes) > 25:
        # Sắp xếp theo diện tích giảm dần, lấy 25 cái to nhất
        valid_boxes = sorted(valid_boxes, key=lambda b: b[2]*b[3], reverse=True)[:25]
    
    # Sắp xếp lại từ trên xuống dưới, trái sang phải để hiển thị đẹp
    valid_boxes.sort(key=lambda b: (b[1] // 40, b[0])) 

    results = []
    
    # Bắt đầu đọc chữ (OCR)
    for (x, y, w, h) in valid_boxes:
        # Cắt vùng ảnh (ROI)
        roi = gray[y:y+h, x:x+w]
        
        # Tiền xử lý cho OCR: Phóng to + Threshold cục bộ
        roi = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, roi_thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Thêm viền trắng (padding) để chữ không sát mép
        roi_final = cv2.copyMakeBorder(roi_thresh, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255])
        
        # Cấu hình chỉ đọc chữ cái và số (White list)
        config = '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = pytesseract.image_to_string(roi_final, config=config)
        cleaned = clean_text(text)
        
        # Chỉ lấy mã có độ dài > 3 ký tự
        if len(cleaned) > 3:
            results.append(cleaned)
            
    return results, len(valid_boxes)

# --- GIAO DIỆN WEB ---
st.title("⚡ Tool Quét Code OKVIP")
st.markdown("---")

uploaded_file = st.file_uploader("Tải ảnh lên (hệ thống tự lọc bỏ nhiễu)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Hiển thị ảnh
    st.image(uploaded_file, caption='Ảnh gốc', use_container_width=True)
    
    if st.button('🚀 BẮT ĐẦU QUÉT', type="primary"):
        with st.spinner('Đang phân tích...'):
            try:
                codes, raw_count = process_image(uploaded_file)
                
                if codes:
                    st.success(f"Đã xử lý {raw_count} vùng ảnh -> Lọc được {len(codes)} mã sạch!")
                    st.markdown("### 👇 Bấm vào bên phải để Copy:")
                    
                    # Hiển thị dạng lưới 2 cột
                    col1, col2 = st.columns(2)
                    for i, code in enumerate(codes):
                        if i % 2 == 0:
                            with col1:
                                st.code(code, language=None)
                        else:
                            with col2:
                                st.code(code, language=None)
                else:
                    st.error("Không tìm thấy mã nào hợp lệ. Thử ảnh rõ hơn hoặc cắt bớt viền thừa.")
                    
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.info("Nếu chạy trên Cloud, hãy chắc chắn file packages.txt đã có tesseract-ocr.")
