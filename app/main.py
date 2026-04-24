import streamlit as st
import sys
import os
import tempfile
import pandas as pd  # Tabloyu güzelleştirmek için

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ifc_handler import karbon_analizi_yap

st.set_page_config(page_title="PreCarbon AI", page_icon="🌍", layout="wide")
st.title("🌍 PreCarbon: AI Destekli Karbon Analiz Paneli")

yuklenen_dosya = st.sidebar.file_uploader("IFC Dosyanızı Seçin", type=["ifc"])

if yuklenen_dosya is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp_file:
        tmp_file.write(yuklenen_dosya.getvalue())
        tmp_dosya_yolu = tmp_file.name

    with st.spinner('Analiz yapılıyor...'):
        # Verileri fonksiyondan alıyoruz
        veriler, toplam = karbon_analizi_yap(tmp_dosya_yolu)

    # Özet Bilgi Kartı
    st.metric(label="Toplam Karbon Ayak İzi", value=f"{toplam:.2f} kg CO2e")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📊 Karbon Dağılım Grafiği")
        st.image(os.path.join(os.path.dirname(__file__), "..", "data", "karbon_grafigi.png"))

    with col2:
        st.subheader("📋 Detaylı Obje Listesi")
        df = pd.DataFrame(veriler)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.success("Analiz başarıyla tamamlandı!")
else:
    st.info("Analiz için lütfen bir IFC dosyası yükleyin.")