import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Expense Tracker Ultimate", page_icon="💰", layout="wide")

# --- 2. การจัดการไฟล์และข้อมูล ---
DB_FILE = "expenses.json"
BUDGET_FILE = "budget.json"

# หมวดหมู่รายจ่าย
EXPENSE_CATEGORIES = {
    "อาหาร": ["มื้อเช้า", "มื้อกลางวัน", "มื้อเย็น", "น้ำ/กาแฟ/ขนม", "วัตถุดิบทำอาหาร", "สังสรรค์"],
    "เดินทาง": ["น้ำมัน", "ทางด่วน/จอดรถ", "รถสาธารณะ", "วิน/แท็กซี่/Grab", "ซ่อมบำรุง/ประกัน"],
    "ของใช้": ["ของใช้ส่วนตัว", "ของใช้ในบ้าน", "เครื่องเขียน/สำนักงาน"],
    "ช้อปปิ้ง": ["เสื้อผ้า/แฟชั่น", "เครื่องสำอาง", "Gadget/ไอที", "ของเล่น/ของสะสม"],
    "บิล/รายเดือน": ["ค่าน้ำ/ค่าไฟ", "ค่าเน็ต/โทรศัพท์", "ค่าเช่า/ผ่อนบ้าน", "ผ่อนรถ", "Netflix/App"],
    "สุขภาพ": ["ค่ายา/หาหมอ", "อาหารเสริม", "ทำฟัน"],
    "อื่นๆ": ["ทำบุญ/บริจาค", "ให้ครอบครัว", "ภาษีสังคม", "อื่นๆ"]
}

# หมวดหมู่รายรับ (เพิ่มใหม่)
INCOME_CATEGORIES = [
    "เงินเดือน", "โบนัส", "งานเสริม/ฟรีแลนซ์", "ดอกเบี้ย/ปันผล", "ขายของ", "ได้รับเงินคืน", "อื่นๆ"
]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # เช็คและเติมค่า type ให้ข้อมูลเก่า (ถ้าไม่มีให้ถือเป็น expense)
                for d in data:
                    if 'type' not in d:
                        d['type'] = 'expense'
                return data
        except:
            return []
    return []

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_budget():
    if os.path.exists(BUDGET_FILE):
        try:
            with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_budget(data):
    with open(BUDGET_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 3. เมนูหลัก (Sidebar) ---
st.sidebar.title("เมนูหลัก")
menu = st.sidebar.radio("ไปที่หน้า:", 
    ["📝 บันทึกรายการ", "📊 สรุปผล (Dashboard)", "🎯 ตั้งงบประมาณ", "✏️ แก้ไขข้อมูล"]
)

# โหลดข้อมูล
data = load_data()
df = pd.DataFrame(data)
if not df.empty and 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

# --- หน้าที่ 1: บันทึกรายการ (รับ/จ่าย) ---
if menu == "📝 บันทึกรายการ":
    st.title("📝 บันทึกรายการ")
    
    with st.container(border=True):
        # เลือกประเภทธุรกรรม
        txn_type = st.radio("ประเภทรายการ", ["รายจ่าย (Expense)", "รายรับ (Income)"], horizontal=True)
        is_income = txn_type == "รายรับ (Income)"

        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=10.0, format="%.2f")
            
            # เลือกหมวดหมู่ตามประเภท
            if is_income:
                main_cat = st.selectbox("ที่มาของรายได้", INCOME_CATEGORIES)
                sub_cat = "-" # รายรับไม่มีหมวดย่อย
            else:
                main_cat = st.selectbox("หมวดหมู่หลัก", list(EXPENSE_CATEGORIES.keys()))
        
        with col2:
            if not is_income:
                sub_cat_options = EXPENSE_CATEGORIES[main_cat]
                sub_cat = st.selectbox("หมวดย่อย", sub_cat_options)
            else:
                st.text_input("หมวดย่อย", value="-", disabled=True)
                
            txn_date = st.date_input("วันที่", datetime.now())
        
        note = st.text_input("บันทึกช่วยจำ (Note)")
        
        if st.button("บันทึกรายการ", type="primary", use_container_width=True):
            if amount > 0:
                new_record = {
                    "date": txn_date.strftime("%Y-%m-%d"),
                    "amount": amount,
                    "type": "income" if is_income else "expense",
                    "category": main_cat,
                    "subcategory": sub_cat,
                    "note": note,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                data.append(new_record)
                save_data(data)
                st.success(f"✅ บันทึก {txn_type}: {amount:,.2f} บาท เรียบร้อย!")
                st.rerun()
            else:
                st.warning("กรุณาระบุจำนวนเงิน")

# --- หน้าที่ 2: สรุปผล (Dashboard) ---
elif menu == "📊 สรุปผล (Dashboard)":
    st.title("📊 สรุปภาพรวมการเงิน")
    
    if not df.empty:
        import plotly.express as px
        
        # ตัวกรองเดือน
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            view_mode = st.selectbox("เลือกช่วงเวลา", ["เดือนนี้", "ทั้งหมด"])
        
        if view_mode == "เดือนนี้":
            today = datetime.now()
            df_view = df[(df['date'].dt.month == today.month) & (df['date'].dt.year == today.year)]
        else:
            df_view = df

        # คำนวณยอดรวม (แยกรับ-จ่าย)
        total_income = df_view[df_view['type'] == 'income']['amount'].sum()
        total_expense = df_view[df_view['type'] == 'expense']['amount'].sum()
        balance = total_income - total_expense

        # แสดง Metrics (3 การ์ดบน)
        m1, m2, m3 = st.columns(3)
        m1.metric("💵 รายรับรวม", f"{total_income:,.2f} บาท", delta_color="normal")
        m2.metric("💸 รายจ่ายรวม", f"{total_expense:,.2f} บาท", delta_color="inverse")
        m3.metric("💰 คงเหลือ (Balance)", f"{balance:,.2f} บาท", delta=f"{balance:,.2f}")

        st.divider()

        # ส่วนแสดงงบประมาณ (Budget Status)
        st.subheader("🎯 สถานะงบประมาณ (Budget Tracker)")
        budgets = load_budget()
        
        if budgets:
            # คำนวณรายจ่ายรายหมวด (เฉพาะ Expense)
            expense_by_cat = df_view[df_view['type'] == 'expense'].groupby('category')['amount'].sum()
            
            for cat, budget_amt in budgets.items():
                if budget_amt > 0:
                    spent = expense_by_cat.get(cat, 0)
                    percent = (spent / budget_amt) * 100
                    remaining = budget_amt - spent
                    
                    st.write(f"**{cat}** (ใช้ไป {spent:,.0f} / {budget_amt:,.0f})")
                    if percent > 100:
                        st.progress(1.0, text=f"⚠️ เกินงบ {remaining:,.0f} บาท")
                    else:
                        st.progress(min(percent/100, 1.0), text=f"เหลือ {remaining:,.0f} บาท")
        else:
            st.info("ยังไม่ได้ตั้งงบประมาณ ไปที่เมนู 'ตั้งงบประมาณ' เพื่อเริ่มใช้งาน")

        st.divider()

        # กราฟ
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("สัดส่วนรายจ่าย")
            df_expense = df_view[df_view['type'] == 'expense']
            if not df_expense.empty:
                fig = px.pie(df_expense, values='amount', names='category', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("ไม่มีรายการจ่าย")
        
        with c2:
            st.subheader("รายรับ vs รายจ่าย (รายวัน)")
            # Group by date and type
            daily = df_view.groupby([df_view['date'].dt.date, 'type'])['amount'].sum().reset_index()
            if not daily.empty:
                fig_bar = px.bar(daily, x='date', y='amount', color='type', barmode='group',
                                 color_discrete_map={'income': '#00CC96', 'expense': '#EF553B'})
                st.plotly_chart(fig_bar, use_container_width=True)

# --- หน้าที่ 3: ตั้งงบประมาณ (Budget) ---
elif menu == "🎯 ตั้งงบประมาณ":
    st.title("🎯 ตั้งงบประมาณรายจ่าย (ต่อเดือน)")
    st.caption("กำหนดวงเงินสูงสุดที่ต้องการใช้ในแต่ละหมวด")
    
    current_budgets = load_budget()
    new_budgets = {}
    
    with st.form("budget_form"):
        cols = st.columns(2)
        for i, cat in enumerate(EXPENSE_CATEGORIES.keys()):
            with cols[i % 2]:
                val = current_budgets.get(cat, 0.0)
                new_budgets[cat] = st.number_input(f"งบหมวด {cat}", min_value=0.0, step=100.0, value=float(val))
        
        submitted = st.form_submit_button("บันทึกงบประมาณ", type="primary")
        if submitted:
            save_budget(new_budgets)
            st.success("บันทึกงบประมาณเรียบร้อย!")

# --- หน้าที่ 4: แก้ไขข้อมูล ---
elif menu == "✏️ แก้ไขข้อมูล":
    st.title("✏️ แก้ไข/ลบ รายการ")
    
    if not df.empty:
        df_editor = df.sort_values(by="timestamp", ascending=False).reset_index(drop=True)
        
        edited_df = st.data_editor(
            df_editor,
            num_rows="dynamic",
            column_config={
                "amount": st.column_config.NumberColumn("จำนวนเงิน", format="%.2f"),
                "date": st.column_config.DateColumn("วันที่", format="YYYY-MM-DD"),
                "type": st.column_config.SelectboxColumn("ประเภท", options=["expense", "income"]),
                "category": st.column_config.SelectboxColumn("หมวดหมู่", options=list(EXPENSE_CATEGORIES.keys()) + INCOME_CATEGORIES),
                "timestamp": st.column_config.TextColumn("Timestamp", disabled=True)
            },
            use_container_width=True,
            hide_index=True
        )

        if st.button("💾 บันทึกการแก้ไขทั้งหมด", type="primary"):
            save_df = edited_df.copy()
            save_df['date'] = save_df['date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else "")
            save_data(save_df.to_dict('records'))
            st.success("บันทึกการแก้ไขเรียบร้อยแล้ว!")
            st.rerun()
    else:
        st.info("ไม่มีข้อมูลให้แก้ไข")
