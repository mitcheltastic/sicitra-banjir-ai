**🌊 Sistem Peringatan Dini Banjir Kabupaten Bandung**

Aplikasi berbasis web ini dirancang untuk memprediksi level siaga banjir di wilayah Kabupaten Bandung (khususnya Dayeuhkolot dan sekitarnya) menggunakan algoritma XGBoost Classifier. Sistem ini mengintegrasikan pemrosesan data sains dengan antarmuka pengguna yang interaktif.

Website versi 1.0 : https://banjir-ieee.streamlit.app/

Website versi 2.0 : https://bandung-floodprediction-ieee.streamlit.app/ 

**🚀 Fitur Utama**
Prediksi Level Siaga: Mengklasifikasikan kondisi air ke dalam 4 level: Normal, Waspada, Siaga, dan Awas berdasarkan Tinggi Muka Air (TMA).
Pemetaan GIS: Visualisasi lokasi stasiun pantauan sungai menggunakan peta interaktif Folium.
Simulasi Real-time: Fitur untuk mensimulasikan data sensor guna melihat respon cepat model terhadap perubahan kondisi cuaca.
Dashboard Performa: Menampilkan metrik akurasi, G-Mean Score, dan Classification Report langsung dari hasil pelatihan model.

🛠️ Teknologi yang Digunakan
1. Python: Bahasa pemrograman utama.
2. Streamlit: Framework untuk antarmuka web.
3. XGBoost: Algoritma Machine Learning untuk klasifikasi multiclass.
4. Scikit-Learn: Untuk preprocessing data dan evaluasi model.
5. Folium: Untuk integrasi peta geografis.

**📋 Struktur File**
1. app.py: File utama aplikasi Streamlit yang berisi logika integrasi model dan antarmuka.
2. style.css: File desain untuk kustomisasi tampilan antarmuka agar lebih profesional.
3. index.html: Struktur elemen HTML statis (opsional/pendukung).
4. XGBoost.ipynb: File riset asli yang berisi proses training dan validasi model.
5. Banjir all - Data Acak (1).csv: Dataset utama yang digunakan untuk melatih model.

**⚙️ Cara Menjalankan**
Pastikan Anda telah menginstal pustaka yang diperlukan:

Bash
pip install streamlit pandas numpy xgboost scikit-learn folium streamlit-folium imbalanced-learn
Letakkan semua file dalam satu folder yang sama.

Jalankan aplikasi melalui terminal/command prompt:

Bash
streamlit run app.py

**📊 Logika Klasifikasi**
Model membagi tingkat bahaya banjir berdasarkan ambang batas Tinggi Muka Air (TMA) sebagai berikut:

> Normal: TMA < 0.57 meter.

> Waspada: 0.57 ≤ TMA < 0.93 meter.


> Siaga: 0.93 ≤ TMA ≤ 1.30 meter.


> Awas: TMA > 1.30 meter.

Dibuat untuk mendukung mitigasi bencana banjir di wilayah Kabupaten Bandung menggunakan pendekatan data sains.
