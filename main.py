import streamlit as st

st.set_page_config(page_title="Tool Lọc Ký Tự", page_icon="✂️")
st.title("✂️ Tool Lọc Ký Tự")

# Ô nhập liệu
text_dau_vao = st.text_area("Dán văn bản vào đây:", height=150)
so_ky_tu = st.number_input("Số ký tự mỗi dòng:", min_value=1, value=6)

if st.button("XỬ LÝ"):
    if text_dau_vao:
        # Lọc lấy chữ và số
        chuoi_sach = "".join(c for c in text_dau_vao if c.isalnum())
        
        # Cắt dòng
        ket_qua = []
        for i in range(0, len(chuoi_sach), so_ky_tu):
            ket_qua.append(chuoi_sach[i : i + so_ky_tu])
            
        # Xuất kết quả
        st.code("\n".join(ket_qua), language='text')
    else:
        st.warning("Chưa nhập gì cả!")
