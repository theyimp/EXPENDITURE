import streamlit as st
import pandas as pd
import os

# ตั้งค่าหน้าเพจ
st.set_page_config(page_title="บันทึกรายรับ-รายจ่าย", layout="wide")

# ชื่อไฟล์สำหรับเก็บข้อมูล (เบื้องต้นใช้ CSV)
DATA_FILE = "finance_data.csv"

# ฟังก์ชันโหลดข้อมูล
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Type", "Description", "Amount"])

# ฟังก์ชันบันทึกข้อมูล
def save_data(date, txt_type, desc, amount):
    df = load_data()
    new_data = pd.DataFrame({
        "Date": [date],
        "Type": [txt_type],
        "Description": [desc],
        "Amount": [amount]
    })
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return df

st.title("💰 แอปบันทึกรายรับ-รายจ่าย")

# --- ส่วนกรอกข้อมูล ---
with st.sidebar:
    st.header("เพิ่มรายการใหม่")
    with st.form("entry_form", clear_on_submit=True):
        date_input = st.date_input("วันที่")
        type_input = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
        desc_input = st.text_input("รายการ (เช่น ค่าข้าว, เงินเดือน)")
        amount_input = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=10.0)
        submitted = st.form_submit_button("บันทึกข้อมูล")

        if submitted:
            save_data(date_input, type_input, desc_input, amount_input)
            st.success("บันทึกเรียบร้อย!")

# --- ส่วนแสดงผล ---
df = load_data()

if not df.empty:
    # คำนวณสรุปยอด
    total_income = df[df["Type"] == "รายรับ"]["Amount"].sum()
    total_expense = df[df["Type"] == "รายจ่าย"]["Amount"].sum()
    balance = total_income - total_expense

    # แสดง Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("รายรับรวม", f"{total_income:,.2f} บาท", delta_color="normal")
    col2.metric("รายจ่ายรวม", f"{total_expense:,.2f} บาท", delta_color="inverse")
    col3.metric("คงเหลือ", f"{balance:,.2f} บาท")

    st.markdown("---")

    # แสดงตารางข้อมูล
    st.subheader("📝 ประวัติรายการ")
    st.dataframe(df, use_container_width=True)
    
    # (Optional) กราฟแสดงสัดส่วน (ถ้ามีข้อมูล)
    if total_expense > 0 or total_income > 0:
        st.subheader("📊 ภาพรวม")
        chart_data = df.groupby("Type")["Amount"].sum()
        st.bar_chart(chart_data)
else:
    st.info("ยังไม่มีข้อมูล กรุณาเพิ่มรายการทางด้านซ้าย")
