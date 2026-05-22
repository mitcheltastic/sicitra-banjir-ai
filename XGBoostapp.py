import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, precision_score, recall_score, f1_score
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.metrics import geometric_mean_score

try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

st.set_page_config(
    page_title="Prediksi Banjir Dayeuhkolot",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- FUNGSI LOGIKA DARI XGBoost.ipynb ---
def tentukan_level_banjir(tma):
    """
    Menentukan level banjir berdasarkan Tinggi Muka Air (TMA) sesuai notebook.
    Threshold:
    - Normal  : < 0.57 m
    - Waspada : 0.57 - 0.93 m
    - Siaga   : 0.93 - 1.30 m
    - Awas    : > 1.30 m
    """
    if tma < 0.57:
        return '0 - Normal'
    elif 0.57 <= tma < 0.93:
        return '1 - Waspada (Siaga 3)'
    elif 0.93 <= tma <= 1.30:
        return '2 - Siaga (Siaga 2)'
    else:
        return '3 - Awas (Siaga 1)'

pemetaan_aliran = {
    # 1. Aliran Citarum (Utama)
    "Dayeuhkolot": "Dayeuhkolot",
    "Situ Cisanti (Hulu Citarum, Kertasari)": "Dayeuhkolot",
    "Cisanti": "Dayeuhkolot", 
    "Kertasari": "Dayeuhkolot",
    "Wangisagara (Majalaya)": "Dayeuhkolot",
    "Majalaya": "Dayeuhkolot",
    "Sapan (Titik temu beberapa anak sungai)": "Dayeuhkolot",
    "Rancamanyar (Baleendah)": "Dayeuhkolot",
    "Nanjung (Margaasih)": "Dayeuhkolot",
    "Cabangbungin (Hilir Citarum)": "Dayeuhkolot",
    "Hantap": "Dayeuhkolot",

    # 2. Aliran Cisangkuy
    "Cipanas - Margamukti (Pangalengan)": "Cipanas - Margamukti",
    "Cipanas": "Cipanas - Margamukti",
    "Cileunca - Wanasari (Pangalengan)": "Cipanas - Margamukti",
    "Cileunca": "Cipanas - Margamukti",
    "Kertamanah - Margamukti (Pangalengan)": "Cipanas - Margamukti",
    "Kertamanah": "Cipanas - Margamukti",
    "Kamasan (Banjaran)": "Cipanas - Margamukti",
    "Pataruman (Baleendah)": "Cipanas - Margamukti",
    "Arjasari": "Cipanas - Margamukti",

    # 3. Aliran Citarik & Cikeruh
    "Cikeruh - Jatiroke": "Cikeruh - Jatiroke",
    "Jatiroke": "Cikeruh - Jatiroke",
    "Cicalengka (Termasuk titik Dampit)": "Cikeruh - Jatiroke",
    "Ciluluk - Cikancung": "Cikeruh - Jatiroke",
    "Ciluluk": "Cikeruh - Jatiroke",
    "Rancaekek": "Cikeruh - Jatiroke",
    "Solokan Jeruk (Titik Citarik)": "Cikeruh - Jatiroke",
    "Mangalayang": "Cikeruh - Jatiroke",

    # 4. Aliran Ciwidey & Cisondari
    "Cisondari - Pasirjambu": "Cisondari - Pasirjambu",
    "Cisondari": "Cisondari - Pasirjambu",
    "Ciwidey": "Cisondari - Pasirjambu",
    "Cibeureum Sadu (Soreang)": "Cisondari - Pasirjambu",
    "Rancaupas": "Cisondari - Pasirjambu",

    # 5. Aliran Lainnya / Lokal
    "Bojongsoang": "Bojongsoang",
    "Cigede - Komplek Radio (Bojongsoang)": "Bojongsoang",
    "Cijalupang - Peundeuy": "Bojongsoang",
    "Cipaku - Paseh": "Bojongsoang",
    "Cipaku Paseh": "Bojongsoang" 
}

koordinat_stasiun = {
    "Dayeuhkolot": [-6.9881, 107.6281],
    "Cipanas - Margamukti": [-7.2185, 107.5565],
    "Cikeruh - Jatiroke": [-6.9450, 107.7680],
    "Cisondari - Pasirjambu": [-7.0680, 107.4780],
    "Bojongsoang": [-6.9740, 107.6400]
}

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("Dayeuhkolot.jpg", use_container_width=True)
    except:
        pass
        
    st.header("🎛️ Parameter Input")
    st.write("Masukkan data untuk dianalisis:")
    
    lokasi_select = st.selectbox("Pilih Lokasi (Kecamatan/Daerah)", options=list(pemetaan_aliran.keys()))
    curah_hujan = st.number_input("Curah Hujan (mm)", min_value=0.0, step=0.1)
    debit_air = st.number_input("Debit Air (m³/s)", min_value=0.0, step=0.1)
    muka_air = st.number_input("Tinggi Muka Air (m)", min_value=0.0, step=0.1)
    # Tinggi banjir tetap ada sebagai input tetapi tidak digunakan fitur model XGB (sesuai ipynb)
    tinggi_banjir_input = st.number_input("Tinggi Genangan Air (m)", min_value=0.0, max_value=5.0, step=0.01)
    
    tombol_prediksi = st.button("🔍 Jalankan Prediksi", use_container_width=True, type="primary")

# --- FUNGSI LOAD DATA & TRAINING (ADAPTASI XGBOOST.IPYNB) ---
@st.cache_resource
def prepare_model(lokasi_terpilih):
    # Menggunakan file utama dari notebook
    filename = "Banjir all - Data Acak (1).csv"
    try:
        df_train = pd.read_csv(filename)
    except:
        return None, None, None, None

    # Cleaning sesuai notebook
    df_train = df_train.drop(columns=['Tanggal', 'Tinggi Banjir', 'Banjir Ya/Tidak'], errors='ignore')
    df_train = df_train.replace('-', np.nan)
    
    kolom_numerik = ['Curah Hujan', 'Debit Air', 'Muka Air']
    for col in kolom_numerik:
        df_train[col] = pd.to_numeric(df_train[col], errors='coerce')
    
    df_train = df_train.ffill().bfill()
    
    # Target Engineering (Level Banjir)
    df_train['Level_Banjir'] = df_train['Muka Air'].apply(tentukan_level_banjir)

    # Encoding Fitur (Kecamatan)
    le_kec = LabelEncoder()
    df_train['Kecamatan'] = le_kec.fit_transform(df_train['Kecamatan'])
    
    # Encoding Target
    le_target = LabelEncoder()
    df_train['Level_Banjir'] = le_target.fit_transform(df_train['Level_Banjir'])

    X = df_train.drop(columns=['Level_Banjir'])
    y = df_train['Level_Banjir']

    # Split untuk metrik
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model XGBoost sesuai notebook
    model_xgb = XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        eval_metric='mlogloss'
    )
    model_xgb.fit(X_train, y_train)
    
    # Hitung metrik untuk tab Performa
    y_pred = model_xgb.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "report": classification_report(y_test, y_pred, target_names=le_target.classes_, output_dict=True),
        "gmean": geometric_mean_score(y_test, y_pred, average='macro'),
        "cm": confusion_matrix(y_test, y_pred)
    }

    return model_xgb, le_kec, le_target, metrics

# Inisialisasi model
model, le_kec, le_target, model_metrics = prepare_model(lokasi_select)

# --- MAIN UI ---
st.title(" Sistem Peringatan Dini Banjir Berbasis Aliran Sungai")
st.markdown("Pantau dan prediksi potensi banjir di wilayah Kabupaten Bandung menggunakan algoritma **XGBoost Classifier**.")

if model is None:
    st.error("File 'Banjir all - Data Acak (1).csv' tidak ditemukan!")
    st.stop()

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Prediksi Level Siaga & Peta", " Simulasi Real-time", "Performa Model AI"])

with tab1:
    col_hasil, col_peta = st.columns([1, 1.2]) 
    
    with col_hasil:
        st.subheader("Hasil Analisis Level Banjir")
        if tombol_prediksi:
            # Preprocessing input
            aliran_induk = pemetaan_aliran.get(lokasi_select, "Dayeuhkolot")
            # Encode lokasi (handle jika lokasi tidak ada di training)
            try:
                kec_encoded = le_kec.transform([aliran_induk])[0]
            except:
                kec_encoded = 0 # Default ke index pertama jika unknown
            
            input_df = pd.DataFrame([[kec_encoded, curah_hujan, debit_air, muka_air]], 
                                   columns=['Kecamatan', 'Curah Hujan', 'Debit Air', 'Muka Air'])
            
            # Prediksi
            res_idx = model.predict(input_df)[0]
            res_label = le_target.inverse_transform([res_idx])[0]
            probs = model.predict_proba(input_df)[0]
            confidence = max(probs)

            st.info(f"ℹ️ Analisis berdasarkan stasiun utama: **{aliran_induk}**")
            
            if "Awas" in res_label:
                st.error(f"🚨 **STATUS: {res_label}**")
                st.write("Segera lakukan evakuasi dan amankan barang berharga!")
            elif "Siaga" in res_label:
                st.warning(f"⚠️ **STATUS: {res_label}**")
                st.write("Waspada, air mulai memasuki pemukiman.")
            elif "Waspada" in res_label:
                st.warning(f"🟡 **STATUS: {res_label}**")
                st.write("Siaga terhadap kenaikan debit air kiriman.")
            else:
                st.success(f"✅ **STATUS: {res_label}**")
                st.write("Kondisi saat ini terpantau aman.")
                
            st.progress(float(confidence), text=f"Tingkat Keyakinan Model: {confidence:.2%}")
            
            st.write("---")
            st.write("**Data Input:**")
            st.write(f"- TMA: {muka_air} m | Curah Hujan: {curah_hujan} mm")
        else:
            st.info("👈 Silakan atur parameter di panel samping dan tekan tombol 'Jalankan Prediksi'.")

    with col_peta:
        st.subheader("Peta Pantauan Sungai (GIS)")
        stasiun_utama = pemetaan_aliran.get(lokasi_select, "Dayeuhkolot")
        
        if HAS_FOLIUM:
            koor = koordinat_stasiun.get(stasiun_utama, [-6.9881, 107.6281]) 
            m = folium.Map(location=koor, zoom_start=13, tiles="CartoDB positron")
            
            folium.Marker(
                koor, 
                popup=f"Stasiun Acuan: {stasiun_utama}", 
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
            
            folium.Circle(
                location=koor,
                radius=1500,
                color='crimson',
                fill=True,
                fill_color='crimson'
            ).add_to(m)

            st_folium(m, width=500, height=350, returned_objects=[])
        else:
            st.warning("Library 'folium' belum terinstal.")

with tab2:
    st.subheader("Pantauan Sensor Virtual (Simulasi Real-time)")
    
    if st.button("Cek Kondisi Terkini (Simulasi)"):
        # Random data simulasi
        sim_hujan = random.uniform(0, 120)
        sim_debit = random.uniform(20, 200)
        sim_muka = random.uniform(0.1, 1.8)
        
        # Prediksi simulasi
        sim_input = pd.DataFrame([[0, sim_hujan, sim_debit, sim_muka]], 
                                columns=['Kecamatan', 'Curah Hujan', 'Debit Air', 'Muka Air'])
        sim_idx = model.predict(sim_input)[0]
        sim_label = le_target.inverse_transform([sim_idx])[0]
        
        wib_now = datetime.utcnow() + timedelta(hours=7)
        
        # UI Box Status
        bg_color = "#ffebeb" if "Awas" in sim_label or "Siaga" in sim_label else "#e8fdf0"
        border_color = "red" if "Awas" in sim_label or "Siaga" in sim_label else "green"
        
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 10px; background-color: {bg_color}; border: 1px solid {border_color};">
            <h3>📢 Status: {sim_label}</h3>
            <p>Diperbarui pada: <b>{wib_now.strftime("%H:%M:%S WIB")}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        k1, k2, k3 = st.columns(3)
        k1.metric("Curah Hujan", f"{sim_hujan:.1f} mm")
        k2.metric("Debit Air", f"{sim_debit:.1f} m³/s")
        k3.metric("Muka Air (TMA)", f"{sim_muka:.2f} m")

with tab3:
    st.subheader("Detail Evaluasi Algoritma XGBoost")
    
    m1, m2 = st.columns(2)
    m1.metric("Akurasi Model", f"{model_metrics['accuracy']:.2%}")
    m2.metric("G-Mean Score", f"{model_metrics['gmean']:.4f}")
    
    st.divider()
    col_cm, col_rep = st.columns([1, 1.5])
    
    with col_cm:
        st.write("**Confusion Matrix:**")
        cm_df = pd.DataFrame(
            model_metrics['cm'], 
            index=[f"Aktual {c}" for c in le_target.classes_],
            columns=[f"Prediksi {c}" for c in le_target.classes_]
        )
        st.table(cm_df)
        
    with col_rep:
        st.write("**Detail Laporan Klasifikasi per Level:**")
        report_df = pd.DataFrame(model_metrics['report']).transpose()
        st.dataframe(report_df.style.format(precision=2))

    st.info("""
    **Catatan Teknis:**
    - Model menggunakan **XGBoost Classifier** dengan parameter `mlogloss`.
    - Klasifikasi dibagi menjadi 4 kelas sesuai standar TMA di notebook.
    - Data dilatih menggunakan dataset: `Banjir all - Data Acak (1).csv`.
    """)
