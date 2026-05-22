import streamlit as st
import pandas as pd
import numpy as np
import random
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from imblearn.metrics import geometric_mean_score
from sklearn.metrics import accuracy_score, classification_report

# Load CSS Kustom
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- FUNGSI DARI XGBOOST.IPYNB ---
def tentukan_level_banjir(tma):
    if tma < 0.57: return '0 - Normal'
    elif 0.57 <= tma < 0.93: return '1 - Waspada (Siaga 3)'
    elif 0.93 <= tma <= 1.30: return '2 - Siaga (Siaga 2)'
    else: return '3 - Awas (Siaga 1)'

@st.cache_resource
def init_model():
    df = pd.read_csv("Banjir all - Data Acak (1).csv")
    df = df.drop(columns=['Tanggal', 'Tinggi Banjir', 'Banjir Ya/Tidak'], errors='ignore').replace('-', np.nan)
    for col in ['Curah Hujan', 'Debit Air', 'Muka Air']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.ffill().bfill()
    
    df['Level_Banjir'] = df['Muka Air'].apply(tentukan_level_banjir)
    le_kec = LabelEncoder()
    df['Kecamatan'] = le_kec.fit_transform(df['Kecamatan'])
    le_target = LabelEncoder()
    df['Level_Banjir'] = le_target.fit_transform(df['Level_Banjir'])
    
    X = df.drop(columns=['Level_Banjir'])
    y = df['Level_Banjir']
    
    model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, eval_metric='mlogloss')
    model.fit(X, y)
    return model, le_kec, le_target

# --- UI STREAMLIT ---
st.title("🌊 Flood Forecasting System")
model, le_kec, le_target = init_model()

# Sidebar & Input
with st.sidebar:
    st.header("Input Parameter")
    kec = st.selectbox("Lokasi", le_kec.classes_)
    hujan = st.number_input("Curah Hujan (mm)", 0.0)
    debit = st.number_input("Debit Air (m3/s)", 0.0)
    tma = st.number_input("Muka Air (m)", 0.0)
    predict_btn = st.button("Analisis")

if predict_btn:
    kec_enc = le_kec.transform([kec])[0]
    input_data = pd.DataFrame([[kec_enc, hujan, debit, tma]], 
                             columns=['Kecamatan', 'Curah Hujan', 'Debit Air', 'Muka Air'])
    
    res_idx = model.predict(input_data)[0]
    res_label = le_target.inverse_transform([res_idx])[0]
    
    # Tampilan Hasil
    st.subheader(f"Hasil Prediksi: {res_label}")
    if "Awas" in res_label or "Siaga" in res_label:
        st.error("Peringatan: Potensi luapan air tinggi!")
    else:
        st.success("Kondisi terpantau aman.")
