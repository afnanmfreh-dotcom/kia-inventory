import streamlit as st
import pandas as pd
import os

# اسم الملف الداخلي لحفظ البيانات للأبد على السيرفر
DB_FILE = "kia_data.csv"

st.set_page_config(page_title="نظام مخزون صيانة كيا", layout="wide")

# تصميم اللوحة بالشكل الأبيض الأنيق
st.title("🚗 لوحة تحكم مخزون قطع الغيار - شركة كيا")
st.write("مرحباً بكِ أيتها المديرة. يتم حفظ وجرد البيانات تلقائياً وبشكل دائم فور الحفظ.")
st.divider()

# تحميل البيانات الحقيقية أو إنشاء بيانات أولية إذا كان أول تشغيل
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame([
        {"ID": "KIA-101", "name": "فلتر زيت سبورتج", "qty": 15, "limit": 5},
        {"ID": "KIA-102", "name": "فحمات فرامل سيراتو", "qty": 3, "limit": 6},
        {"ID": "KIA-103", "name": "زيت محرك 5W30", "qty": 20, "limit": 10}
    ])
    df_init.to_csv(DB_FILE, index=False)

# قراءة أحدث البيانات دائماً من الملف الثابت
df_current = pd.read_csv(DB_FILE)
df_current['ID'] = df_current['ID'].astype(str)
inventory = df_current.to_dict(orient="records")

# 1. نظام التنبيهات العاجلة باللون الأحمر للقطع المطلوبة
alerts = [item for item in inventory if int(item["qty"]) <= int(item["limit"])]
if alerts:
    st.subheader("🚨 قطع أوشكت على النفاذ (مطلوبة فوراً)")
    for item in alerts:
        st.error(f"❌ تنبيه: القطعة ({item['name']}) [كود: {item['ID']}] متبقي منها: {item['qty']} قطع فقط! (حد الأمان: {item['limit']})")
else:
    st.success("✅ جميع القطع متوفرة بكميات ممتازة فوق حد الأمان.")

st.divider()

# 2. محرك البحث الذكي (بحث بالاسم والكود معاً)
st.subheader("🔍 البحث السريع في المخزن")
search_query = st.text_input("ادخلي اسم القطعة أو رقم الكود (ID) للبحث الفوري:", placeholder="مثال: فلتر أو KIA-101")

# 3. عرض جدول المخزن والفلترة بناءً على البحث
st.subheader("📦 جدول جرد وإدارة المخزون الحالي")

filtered_items = []
for item in inventory:
    if search_query.strip() == "" or search_query.lower() in str(item["ID"]).lower() or search_query.lower() in str(item["name"]).lower():
        filtered_items.append(item)

if filtered_items:
    df_display = pd.DataFrame(filtered_items)
    df_display.columns = ["كود القطعة (ID)", "اسم قطعة الغيار", "الكمية الحالية", "حد الأمان للمخزون"]
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("ℹ️ لا توجد نتائج مطابقة لعملية البحث.")

st.divider()

# 4. قسم الإضافة اليدوية والتعديل والحفظ الدائم الثابت
st.subheader("➕ إضافة قطعة جديدة أو تعديل كمية الحالية")
col1, col2 = st.columns(2)
with col1:
    item_id = st.text_input("رقم القطعة (ID)")
    item_name = st.text_input("اسم قطعة الغيار")
with col2:
    item_qty = st.number_input("الكمية المتوفرة حالياً", min_value=0, value=10)
    item_limit = st.number_input("حد الأمان (التنبيه)", min_value=0, value=5)

if st.button("💾 حفظ البيانات وتحديث المخزن بشكل دائم"):
    if item_id and item_name:
        # تعديل القطعة لو موجودة أو إضافتها لو جديدة
        if item_id.strip() in df_current['ID'].values:
            df_current.loc[df_current['ID'] == item_id.strip(), ['name', 'qty', 'limit']] = [item_name, item_qty, item_limit]
        else:
            new_row = pd.DataFrame([{"ID": str(item_id), "name": item_name, "qty": int(item_qty), "limit": int(item_limit)}])
            df_current = pd.concat([df_current, new_row], ignore_index=True)
        
        # حفظ فوري ودائم داخل الملف الثابت على السيرفر لضمان عدم الضياع عند الإغلاق
        df_current.to_csv(DB_FILE, index=False)
        st.success("🎉 تم حفظ البيانات بنجاح في مخزن النظام وتحديث لوحة التحكم!")
        st.rerun()
    else:
        st.warning("⚠️ يرجى كتابة كود القطعة واسمها أولاً لحفظها.")

