import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="نظام مخزون صيانة كيا", layout="wide")

# عنوان اللوحة بالشكل الأبيض الأنيق
st.title("🚗 لوحة تحكم مخزون قطع الغيار - شركة كيا")
st.write("مرحباً بكِ أيتها المديرة. يتم جرد وحفظ البيانات تلقائياً وبشكل دائم عبر Google Sheets.")
st.divider()

# رابط جدول جوجل شيت الخاص بكِ
sheet_url = "https://docs.google.com/spreadsheets/d/1vdiC8pmpMA0v1cvLBRxOSAbKG8Nm12arLamaZmdUssA/edit?usp=sharing"

# الاتصال بجدول جوجل وقراءة البيانات الحقيقية فوراً
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=sheet_url, ttl="0m")
    
    # تحويل الجدول لقائمة ليسهل قراءتها وتعديلها
    inventory = df.to_dict(orient="records")
except Exception as e:
    st.error("⚠️ خطأ في الاتصال بجدول جوجل، يرجى التأكد من أن خيار المشاركة متاح لجميع من يملك الرابط.")
    inventory = []

# 1. نظام التنبيهات العاجلة باللون الأحمر
if inventory:
    alerts = [item for item in inventory if int(item["qty"]) <= int(item["limit"])]
    if alerts:
        st.subheader("🚨 قطع أوشكت على النفاذ (مطلوبة فوراً)")
        for item in alerts:
            st.error(f"❌ تنبيه: القطعة ({item['name']}) [كود: {item['ID']}] متبقي منها: {item['qty']} قطع فقط! (حد الأمان: {item['limit']})")
    else:
        st.success("✅ جميع القطع متوفرة بكميات ممتازة فوق حد الأمان.")

st.divider()

# 2. محرك البحث الذكي (بحث بالاسم والكود)
st.subheader("🔍 البحث السريع في المخزن")
search_query = st.text_input("ادخلي اسم القطعة أو رقم الكود (ID) للبحث الفوري:", placeholder="مثال: فلتر أو 873465")

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

# 4. قسم الإضافة اليدوية والتعديل والحفظ الدائم
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
        # قراءة أحدث نسخة من الجدول أولاً قبل التحديث لتجنب أي تضارب
        df_current = conn.read(spreadsheet=sheet_url, ttl="0m")
        
        # التأكد من نوع البيانات لتحويلها لنصوص للمقارنة
        df_current['ID'] = df_current['ID'].astype(str)
        
        # فحص إذا كانت القطعة موجودة مسبقاً لتعديلها، أو إضافتها كجديدة
        if item_id.strip() in df_current['ID'].values:
            df_current.loc[df_current['ID'] == item_id.strip(), ['name', 'qty', 'limit']] = [item_name, item_qty, item_limit]
        else:
            new_row = pd.DataFrame([{"ID": str(item_id), "name": item_name, "qty": int(item_qty), "limit": int(item_limit)}])
            df_current = pd.concat([df_current, new_row], ignore_index=True)
        
        # كتابة وتحديث جدول جوجل شيت الأصلي بشكل فوري ودائم للأبد
        conn.update(spreadsheet=sheet_url, data=df_current)
        st.success("🎉 تم حفظ البيانات بنجاح داخل Google Sheets وتحديث الموقع!")
        st.rerun()
    else:
        st.warning("⚠️ يرجى كتابة كود القطعة واسمها أولاً لحفظها.")


