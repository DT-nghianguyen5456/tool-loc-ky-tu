import streamlit as st
from PIL import Image
import pytesseract

# Cấu hình trang
st.set_page_config(page_title="Tool Lọc Code Đa Năng", page_icon="⚡")
st.title("⚡ Tool Quét Ảnh & Nhập Tay")

# --- PHẦN 1: UPLOAD ẢNH ---
st.info("Cách dùng: Bạn có thể Upload ảnh để lấy chữ, HOẶC nhập tay, HOẶC làm cả hai!")

uploaded_file = st.file_uploader("1. Chọn ảnh (Nếu có)", type=['png', 'jpg', 'jpeg'])

# Biến để kiểm soát việc quét ảnh (tránh quét lại nhiều lần khi bấm nút khác)
if 'last_uploaded_file' not in st.session_state:
    st.session_state['last_uploaded_file'] = None

# Xử lý khi có file mới
if uploaded_file is not None:
    # Chỉ xử lý nếu đây là file mới (khác file cũ)
    if uploaded_file != st.session_state['last_uploaded_file']:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption='Ảnh vừa tải lên', width=300)
            
            with st.spinner('Đang đọc chữ từ ảnh...'):
                text_ocr = pytesseract.image_to_string(image)
            
            if text_ocr.strip():
                st.toast("Đã quét xong! Đang cập nhật văn bản...", icon="✅")
                
                # --- KHẮC PHỤC LỖI TẠI ĐÂY ---
                # Cập nhật trực tiếp vào 'input_box' để ô text thay đổi ngay lập tức
                current_text = st.session_state.get('input_box', "")
                st.session_state['input_box'] = current_text + "\n" + text_ocr
                
                # Lưu lại file này là đã xử lý
                st.session_state['last_uploaded_file'] = uploaded_file
            else:
                st.warning("Ảnh này không có chữ hoặc quá mờ!")
                
        except Exception as e:
            st.error(f"Lỗi đọc ảnh: {e}")

# --- PHẦN 2: Ô NHẬP LIỆU CHÍNH ---
st.write("---")

# Khởi tạo giá trị mặc định cho ô input nếu chưa có
if 'input_box' not in st.session_state:
    st.session_state['input_box'] = ""

noi_dung_cuoi = st.text_area(
    "2. Nội dung cần xử lý (Bạn có thể sửa hoặc paste thêm vào đây):",
    key="input_box", # Key này liên kết trực tiếp với session_state['input_box']
    height=200
)

# --- PHẦN 3: XỬ LÝ ---
col1, col2 = st.columns([1, 2])
with col1:
    so_ky_tu = st.number_input("Số ký tự ngắt dòng:", min_value=1, value=6)
with col2:
    st.write("") 
    st.write("")
    nut_bam = st.button("🚀 LỌC & XẾP NGAY", type="primary", use_container_width=True)

if nut_bam:
    if noi_dung_cuoi:
        # 1. Lọc sạch (Chỉ lấy chữ và số)
        chuoi_sach = "".join(k for k in noi_dung_cuoi if k.isalnum())
        
        if not chuoi_sach:
            st.error("Không tìm thấy ký tự Code nào hợp lệ!")
        else:
            # 2. Cắt dòng
            ket_qua = []
            for i in range(0, len(chuoi_sach), so_ky_tu):
                ket_qua.append(chuoi_sach[i : i + so_ky_tu])
            
            # 3. Xuất kết quả
            st.success(f"Xong! Tổng cộng: {len(chuoi_sach)} ký tự.")
            final_text = "\n".join(ket_qua)
            st.code(final_text, language='text')
    else:
        st.warning("Chưa có nội dung nào! Hãy up ảnh hoặc nhập chữ vào ô trên.")
