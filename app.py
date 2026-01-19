import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import plotly.express as px

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Expense Tracker Pro", page_icon="💰", layout="wide")

# --- 2. ข้อมูลและการจัดการไฟล์ ---
DB_FILE = "expenses.json"

CATEGORIES = {
    "อาหาร": ["มื้อเช้า", "มื้อกลางวัน", "มื้อเย็น", "น้ำ/กาแฟ/ขนม", "วัตถุดิบทำอาหาร", "สังสรรค์"],
    "เดินทาง": ["น้ำมัน", "ทางด่วน/จอดรถ", "รถสาธารณะ", "วิน/แท็กซี่/Grab", "ซ่อมบำรุง/ประกัน"],
    "ของใช้": ["ของใช้ส่วนตัว", "ของใช้ในบ้าน", "เครื่องเขียน/สำนักงาน"],
    "ช้อปปิ้ง": ["เสื้อผ้า/แฟชั่น", "เครื่องสำอาง", "Gadget/ไอที", "ของเล่น/ของสะสม"],
    "บิล/รายเดือน": ["ค่าน้ำ/ค่าไฟ", "ค่าเน็ต/โทรศัพท์", "ค่าเช่า/ผ่อนบ้าน", "ผ่อนรถ", "Netflix/App"],
    "สุขภาพ": ["ค่ายา/หาหมอ", "อาหารเสริม", "ทำฟัน"],
    "อื่นๆ": ["ทำบุญ/บริจาค", "ให้ครอบครัว", "ภาษีสังคม", "อื่นๆ"]
}

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except:
            return []
    return []

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 3. ส่วนเมนู (Sidebar) ---
st.sidebar.title("เมนูหลัก")
menu = st.sidebar.radio("ไปที่หน้า:", ["📝 บันทึกรายจ่าย", "📊 สรุปผล (Dashboard)", "✏️ แก้ไขข้อมูล"])

# โหลดข้อมูลเตรียมไว้
data = load_data()
df = pd.DataFrame(data)

# --- หน้าที่ 1: บันทึกรายจ่าย ---
if menu == "📝 บันทึกรายจ่าย":
    st.title("📝 บันทึกรายจ่ายใหม่")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=10.0, format="%.2f")
            main_cat = st.selectbox("หมวดหมู่หลัก", list(CATEGORIES.keys()))
        
        with col2:
            sub_cat_options = CATEGORIES[main_cat]
            sub_cat = st.selectbox("หมวดย่อย", sub_cat_options)
            txn_date = st.date_input("วันที่", datetime.now())
        
        note = st.text_input("บันทึกช่วยจำ (Note)")
        
        if st.button("บันทึกรายการ", type="primary", use_container_width=True):
            if amount > 0:
                new_record = {
                    "date": txn_date.strftime("%Y-%m-%d"),
                    "amount": amount,
                    "category": main_cat,
                    "subcategory": sub_cat,
                    "note": note,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                data.append(new_record)
                save_data(data)
                st.success("✅ บันทึกเรียบร้อย!")
            else:
                st.warning("กรุณาระบุจำนวนเงิน")

# --- หน้าที่ 2: สรุปผล (Dashboard) ---
elif menu == "📊 สรุปผล (Dashboard)":
    st.title("📊 สรุปภาพรวมการใช้เงิน")
    
    if not df.empty:
        # แปลงข้อมูลวันที่เพื่อให้คำนวณได้
        df['date'] = pd.to_datetime(df['date'])
        
        # ตัวกรองเดือน (Filter)
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            view_mode = st.selectbox("เลือกมุมมอง", ["เดือนนี้", "ทั้งหมด"])
        
        # Filter Logic
        if view_mode == "เดือนนี้":
            today = datetime.now()
            df_view = df[(df['date'].dt.month == today.month) & (df['date'].dt.year == today.year)]
        else:
            df_view = df

        # Metrics 3 ตัวบน
        total_exp = df_view['amount'].sum()
        avg_exp = df_view['amount'].mean() if not df_view.empty else 0
        count_txn = len(df_view)

        m1, m2, m3 = st.columns(3)
        m1.metric("ยอดรวม", f"{total_exp:,.2f} บาท")
        m2.metric("เฉลี่ยต่อรายการ", f"{avg_exp:,.2f} บาท")
        m3.metric("จำนวนรายการ", f"{count_txn} ครั้ง")

        st.divider()

        # Charts
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("สัดส่วนตามหมวดหมู่")
            if not df_view.empty:
                fig_pie = px.pie(df_view, values='amount', names='category', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with c2:
            st.subheader("แนวโน้มการใช้จ่าย (รายวัน)")
            if not df_view.empty:
                # Group by Date
                daily_sum = df_view.groupby(df_view['date'].dt.date)['amount'].sum().reset_index()
                fig_bar = px.bar(daily_sum, x='date', y='amount', color='amount')
                st.plotly_chart(fig_bar, use_container_width=True)
                
    else:
        st.info("ยังไม่มีข้อมูลรายการ")

# --- หน้าที่ 3: แก้ไขข้อมูล (Editor) ---
elif menu == "✏️ แก้ไขข้อมูล":
    st.title("✏️ แก้ไข/ลบ รายการ")
    st.caption("คุณสามารถแก้ตัวเลข แก้คำผิด หรือลบแถวได้จากตารางด้านล่างโดยตรง แล้วกดปุ่ม 'บันทึกการแก้ไข'")

    if not df.empty:
        # เตรียม DataFrame สำหรับ Editor
        # เรียงลำดับจากใหม่ไปเก่า
        df_editor = df.sort_values(by="timestamp", ascending=False).reset_index(drop=True)

        # สร้าง Data Editor
        edited_df = st.data_editor(
            df_editor,
            num_rows="dynamic", # อนุญาตให้เพิ่ม/ลบแถวได้
            column_config={
                "amount": st.column_config.NumberColumn("จำนวนเงิน", format="%.2f"),
                "date": st.column_config.DateColumn("วันที่", format="YYYY-MM-DD"),
                "category": st.column_config.SelectboxColumn("หมวดหมู่", options=list(CATEGORIES.keys())),
                "subcategory": st.column_config.TextColumn("หมวดย่อย"),
                "note": st.column_config.TextColumn("Note"),
                "timestamp": st.column_config.TextColumn("Timestamp (Auto)", disabled=True)
            },
            use_container_width=True,
            hide_index=True
        )

        # ปุ่มบันทึก (สำคัญมาก)
        if st.button("💾 บันทึกการแก้ไขทั้งหมด", type="primary"):
            # แปลง DataFrame กลับเป็น List of Dict เพื่อบันทึก JSON
            # ต้องแปลง Date Object กลับเป็น String ก่อน
            save_df = edited_df.copy()
            save_df['date'] = save_df['date'].astype(str) 
            
            # บันทึก
            save_data(save_df.to_dict('records'))
            st.success("บันทึกการแก้ไขเรียบร้อยแล้ว!")
            st.rerun()
            
    else:
        st.info("ไม่มีข้อมูลให้แก้ไข")

