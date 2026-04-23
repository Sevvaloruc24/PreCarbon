import ifcopenshell
import ifcopenshell.geom
import os
import json
import matplotlib.pyplot as plt


def karbon_analizi_yap(dosya_yolu):
    # 1. Katsayıları Yükle
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "carbon_factors.json")
    with open(json_path, "r", encoding="utf-8") as f:
        katsayilar = json.load(f)["materials"]

    # 2. IFC ve Geometri Ayarları
    settings = ifcopenshell.geom.settings()
    model = ifcopenshell.open(dosya_yolu)
    objeler = model.by_type("IfcBuildingElementProxy")

    isimler_listesi = []
    karbon_degerleri = []

    print(f"\n--- 🚀 AKILLI GEOMETRİ VE KARBON ANALİZİ ---")

    for i, obje in enumerate(objeler, 1):
        isim = (obje.Name or f"Obje_{i}").upper()

        # --- A SEÇENEĞİ: BOUNDING BOX HACİM HESABI ---
        try:
            shape = ifcopenshell.geom.create_shape(settings, obje)
            # Objenin köşe noktalarından kutu boyutlarını buluyoruz
            verts = shape.geometry.verts
            x_coords = verts[0::3];
            y_coords = verts[1::3];
            z_coords = verts[2::3]

            genislik = max(x_coords) - min(x_coords)
            derinlik = max(y_coords) - min(y_coords)
            yukseklik = max(z_coords) - min(z_coords)
            hacim = genislik * derinlik * yukseklik
        except:
            hacim = 1.0  # Geometri okunamazsa güvenli liman

        # Karbon Hesaplama
        faktor = katsayilar["BETONFERTIGTEIL"]["factor"] if "BETON" in isim else katsayilar["GENEL"]["factor"]
        obje_karbon = hacim * faktor

        # Grafik için verileri listeye ekle
        isimler_listesi.append(f"{i}-{isim[:10]}")
        karbon_degerleri.append(obje_karbon)

        print(f"{i}. {isim[:15]:<15} | Hacim: {hacim:.3f} m3 | Karbon: {obje_karbon:.2f} kg")

    # --- B SEÇENEĞİ: GRAFİK OLUŞTURMA ---
    plt.figure(figsize=(10, 6))
    plt.bar(isimler_listesi, karbon_degerleri, color='skyblue')
    plt.xlabel('Objeler')
    plt.ylabel('Karbon Ayak İzi (kg CO2)')
    plt.title('PreCarbon: Obje Bazlı Karbon Dağılımı')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Grafiği kaydet ve göster
    plt.savefig(os.path.join(os.path.dirname(__file__), "..", "data", "karbon_grafigi.png"))
    print(f"\n📊 Grafik 'data/karbon_grafigi.png' olarak kaydedildi!")
    plt.show()


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "..", "data", "deneme.ifc")
    karbon_analizi_yap(path)