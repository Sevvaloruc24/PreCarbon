import sys
import os

# src klasöründeki kodlara ulaşabilmek için yolu tanıtıyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ifc_handler import karbon_analizi_yap


def uygulama_baslat():
    print("=" * 50)
    print("🌍 PRECARBON: ERKEN AŞAMA KARBON TAHMİN ARACI")
    print("=" * 50)

    # Veri dosyamızın yolu
    ifc_yolu = os.path.join(os.path.dirname(__file__), "..", "data", "deneme.ifc")

    if os.path.exists(ifc_yolu):
        print(f"🔍 Analiz Ediliyor: {os.path.basename(ifc_yolu)}")
        karbon_analizi_yap(ifc_yolu)
    else:
        print("❌ Hata: 'data' klasöründe 'deneme.ifc' dosyası bulunamadı!")

    print("\n" + "=" * 50)
    print("✅ Analiz Tamamlandı.")


if __name__ == "__main__":
    uygulama_baslat()