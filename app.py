import streamlit as st
import pandas as pd

# إعداد الصفحة لتكون بيضاء ونظيفة بشكل افتراضي ومتوافقة مع الجوال والكمبيوتر
st.set_page_config(
    page_title="نظام مخزون صيانة كيا", 
    layout="wide"
)

# عنوان رئيسي بسيط وأنيق
st.title("🚗 لوحة تحكم مخزون قطع الغيار - شركة كيا")
st.write("مرحباً بكِ أيتها المديرة. يمكنكِ متابعة المخزون والبحث وتحديث البيانات من هنا.")
st.divider()

# قاعدة البيانات داخل ذاكرة الموقع
if 'inventory' not in st.session_state:
    st.session_state.inventory = [
        {"ID": "KIA-101", "name": "فلتر زيت سبورتج", "qty": 15, "limit": 5},
        {"ID": "KIA-102", "name": "فحمات فرامل سيراتو", "qty": 3, "limit": 6},
        {"ID": "KIA-103", "name": "زيت محرك 5W30", "qty": 20, "limit": 10},
        {"ID": "KIA-104", "name": "بواجي أوبتيما", "qty": 1, "limit": 4}
    ]

# 1. التنبيهات العاجلة (تظهر باللون الأحمر الصريح فقط عند الحاجة)
alerts = [item for item in st.session_state.inventory if item["qty"] <= item["limit"]]

if alerts:
    st.subheader("🚨 قطع أوشكت على النفاذ (مطلوبة فوراً)")
    for item in alerts:
        st.error(f"❌ تنبيه: القطعة ({item['name']}) [كود: {item['ID']}] متبقي منها: {item['qty']} قطع فقط! (حد الأمان: {item['limit']})")
else:
    st.success("✅ جميع القطع متوفرة بكميات ممتازة فوق حد الأمان.")

st.divider()

# 2. محرك البحث الذكي (ابحثي باسم القطعة أو الكود في نفس الخانة)
st.subheader("🔍 البحث السريع في المخزن")
search_query = st.text_input("ادخلي اسم القطعة أو رقم الكود (ID) للبحث الفوري:", placeholder="مثال: فلتر أو KIA-102")

# 3. عرض جدول المخزن والفلترة
st.subheader("📦 جدول جرد وإدارة المخزون الحالي")

filtered_items = []
for item in st.session_state.inventory:
    if search_query.strip() == "" or search_query.lower() in item["ID"].lower() or search_query.lower() in item["name"].lower():
        filtered_items.append(item)

if filtered_items:
    df_display = pd.DataFrame(filtered_items)
    df_display.columns = ["كود القطعة (ID)", "اسم قطعة الغيار", "الكمية الحالية", "حد الأمان للمخزون"]
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("ℹ️ لا توجد نتائج مطابقة لعملية البحث.")

st.divider()

# 4. قسم الإضافة والتعديل للمديرة
st.subheader("➕ إضافة قطعة جديدة أو تعديل كمية الحالية")
col1, col2 = st.columns(2)
with col1:
    item_id = st.text_input("رقم القطعة (ID)")
    item_name = st.text_input("اسم قطعة الغيار")
with col2:
    item_qty = st.number_input("الكمية المتوفرة حالياً", min_value=0, value=10)
    item_limit = st.number_input("حد الأمان (التنبيه)", min_value=0, value=5)

if st.button("💾 حفظ البيانات وتحديث المخزن"):
    if item_id and item_name:
        updated = False
        for item in st.session_state.inventory:
            if item["ID"].strip().lower() == item_id.strip().lower():
                item["name"] = item_name
                item["qty"] = item_qty
                item["limit"] = item_limit
                updated = True
        if not updated:
            st.session_state.inventory.append({"ID": item_id, "name": item_name, "qty": item_qty, "limit": item_limit})
        st.success("تم حفظ البيانات وتحديث لوحة التحكم بنجاح!")
        st.rerun()
    else:
        st.warning("⚠️ يرجى كتابة كود القطعة واسمها أولاً لحفظها.")
