import ifcopenshell
import os
import json


def karbon_analizi_yap(dosya_yolu):
    # 1. Önce katsayıları JSON'dan yükleyelim
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "carbon_factors.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            katsayilar = json.load(f)["materials"]
    except Exception as e:
        print(f"❌ JSON katsayı dosyası okunamadı: {e}")
        return

    # 2. IFC modelini açalım
    try:
        model = ifcopenshell.open(dosya_yolu)
        objeler = model.by_type("IfcBuildingElementProxy")

        toplam_karbon = 0
        print(f"\n--- 📊 PRECARBON ANALİZ RAPORU ---")

        for i, obje in enumerate(objeler, 1):
            isim = (obje.Name or "").upper()

            # Basit eşleştirme mantığı
            if "BETONFERTIGTEIL" in isim:
                faktör = katsayilar["BETONFERTIGTEIL"]["factor"]
                malzeme = "Prefabrik Beton"
            else:
                faktör = katsayilar["GENEL"]["factor"]
                malzeme = "Tanımsız/Genel"

            toplam_karbon += faktör
            print(f"{i}. Obje: {isim[:20]} | Malzeme: {malzeme} | Karbon: {faktör} kg")

        print("-" * 50)
        print(f"BİNA TOPLAM KARBON AYAK İZİ: {toplam_karbon} kg CO2")

    except Exception as e:
        print(f"❌ IFC Analiz hatası: {e}")


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "..", "data", "deneme.ifc")
    karbon_analizi_yap(path)