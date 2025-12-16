import streamlit as st
from PIL import Image
import pytesseract

# Cấu hình trang
st.set_page_config(page_title="Tool Lọc Code Đa Năng", page_icon="⚡")
st.title("⚡ Tool Quét Ảnh & Nhập Tay")

# Khởi tạo kho chứa dữ liệu (session_state) nếu chưa có
if 'noi_dung_chinh' not in st.session_state:
    st.session_state['noi_dung_chinh'] = ""

# --- PHẦN 1: UPLOAD ẢNH ---
st.info("Cách dùng: Bạn có thể Upload ảnh để lấy chữ, HOẶC nhập tay, HOẶC làm cả hai!")

uploaded_file = st.file_uploader("1. Chọn ảnh (Nếu có)", type=['png', 'jpg', 'jpeg'])

# Xử lý khi có ảnh mới được upload
if uploaded_file is not None:
    # Logic: Chỉ quét nếu đây là ảnh mới (để tránh quét lại liên tục)
    # Dùng tên file để check đơn giản
    file_id = f"processed_{uploaded_file.name}"
    
    if file_id not in st.session_state:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption='Ảnh vừa tải lên', width=300)
            
            with st.spinner('Đang đọc chữ từ ảnh...'):
                # Quét chữ
                text_ocr = pytesseract.image_to_string(image)
                
            if text_ocr.strip():
                st.toast("Đã quét xong! Chữ đã được thêm vào ô bên dưới.", icon="✅")
                # NỐI THÊM vào nội dung đang có (hoặc điền mới)
                st.session_state['noi_dung_chinh'] += "\n" + text_ocr
                # Đánh dấu là đã xử lý file này rồi
                st.session_state[file_id] = True
            else:
                st.warning("Ảnh này không có chữ hoặc quá mờ!")
        except Exception as e:
            st.error(f"Lỗi đọc ảnh: {e}")

# --- PHẦN 2: Ô NHẬP LIỆU CHÍNH (VỪA HIỆN TEXT ẢNH, VỪA NHẬP TAY) ---
st.write("---")
noi_dung_cuoi = st.text_area(
    "2. Nội dung cần xử lý (Bạn có thể sửa hoặc paste thêm vào đây):",
    value=st.session_state['noi_dung_chinh'],
    height=200,
    key="input_box" # Key để đồng bộ dữ liệu
)

# Cập nhật ngược lại session_state khi người dùng gõ tay
st.session_state['noi_dung_chinh'] = noi_dung_cuoi

# --- PHẦN 3: XỬ LÝ ---
col1, col2 = st.columns([1, 2])
with col1:
    so_ky_tu = st.number_input("Số ký tự ngắt dòng:", min_value=1, value=6)
with col2:
    st.write("") # Dòng trống để căn chỉnh
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
