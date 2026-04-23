import ifcopenshell
import ifcopenshell.geom
import os
import json
import matplotlib.pyplot as plt


def karbon_analizi_yap(dosya_yolu):
    # 1. Katsayıları JSON'dan Yükle
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "carbon_factors.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            katsayilar = data["materials"]
    except Exception as e:
        print(f"❌ JSON katsayı dosyası okunamadı: {e}")
        return

    # 2. IFC ve Geometri Ayarları
    settings = ifcopenshell.geom.settings()
    try:
        model = ifcopenshell.open(dosya_yolu)
        objeler = model.by_type("IfcBuildingElementProxy")
    except Exception as e:
        print(f"❌ IFC dosyası açılamadı: {e}")
        return

    isimler_listesi = []
    karbon_degerleri = []
    toplam_karbon = 0

    print(f"\n--- 🚀 GELİŞMİŞ MALZEME VE KARBON ANALİZİ ---")
    print(f"{'No':<3} | {'Obje İsmi':<15} | {'Malzeme':<10} | {'Hacim':<8} | {'Karbon':<10}")
    print("-" * 65)

    for i, obje in enumerate(objeler, 1):
        isim = (obje.Name or f"Obje_{i}").upper()

        # --- HACİM HESABI (Bounding Box) ---
        try:
            shape = ifcopenshell.geom.create_shape(settings, obje)
            verts = shape.geometry.verts
            x_coords = verts[0::3];
            y_coords = verts[1::3];
            z_coords = verts[2::3]
            hacim = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords)) * (max(z_coords) - min(z_coords))
        except:
            hacim = 1.0

            # --- GELİŞMİŞ MALZEME TAHMİN MEKANİZMASI ---
        if any(keyword in isim for keyword in ["BETON", "CONCRETE", "BETONFERTIGTEIL"]):
            faktor = katsayilar["BETON"]["factor"]
            malzeme_etiketi = "Beton"
        elif any(keyword in isim for keyword in ["STEEL", "CELIK", "IRON"]):
            faktor = katsayilar["STEEL"]["factor"]
            malzeme_etiketi = "Çelik"
        elif any(keyword in isim for keyword in ["GLASS", "CAM"]):
            faktor = katsayilar["GLASS"]["factor"]
            malzeme_etiketi = "Cam"
        elif any(keyword in isim for keyword in ["WOOD", "AHSAP", "TIMBER"]):
            faktor = katsayilar["WOOD"]["factor"]
            malzeme_etiketi = "Ahşap"
        else:
            faktor = katsayilar["GENEL"]["factor"]
            malzeme_etiketi = "Genel"

        obje_karbon = hacim * faktor
        toplam_karbon += obje_karbon

        # Grafik için verileri kaydet
        isimler_listesi.append(f"{i}-{malzeme_etiketi}")
        karbon_degerleri.append(obje_karbon)

        print(f"{i:<3} | {isim[:15]:<15} | {malzeme_etiketi:<10} | {hacim:<6.2f} m3 | {obje_karbon:>8.2f} kg")

    print("-" * 65)
    print(f"BİNA TOPLAM KARBON AYAK İZİ: {toplam_karbon:.2f} kg CO2")

    # --- GRAFİK OLUŞTURMA ---
    plt.figure(figsize=(12, 6))
    plt.bar(isimler_listesi, karbon_degerleri, color='teal')
    plt.xlabel('Objeler (Malzeme Tipleri)')
    plt.ylabel('Karbon Ayak İzi (kg CO2)')
    plt.title('PreCarbon: Çoklu Malzeme Bazlı Karbon Analizi')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Grafiği kaydet ve göster
    grafik_yolu = os.path.join(os.path.dirname(__file__), "..", "data", "karbon_grafigi.png")
    plt.savefig(grafik_yolu)
    print(f"\n📊 Grafik güncellendi ve '{grafik_yolu}' konumuna kaydedildi!")
    plt.show()


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "..", "data", "deneme.ifc")
    karbon_analizi_yap(path)