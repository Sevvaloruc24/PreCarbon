import ifcopenshell
import ifcopenshell.geom
import os
import json
import matplotlib.pyplot as plt


def karbon_analizi_yap(dosya_yolu):
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "carbon_factors.json")
    with open(json_path, "r", encoding="utf-8") as f:
        katsayilar = json.load(f)["materials"]

    settings = ifcopenshell.geom.settings()
    model = ifcopenshell.open(dosya_yolu)
    objeler = model.by_type("IfcBuildingElementProxy")

    isimler_listesi = []
    karbon_degerleri = []
    toplam_karbon = 0

    print(f"\n--- 🧠 AI DESTEKLİ MALZEME TAHMİN RAPORU ---")

    for i, obje in enumerate(objeler, 1):
        isim = (obje.Name or "").upper()

        # Geometri ve Hacim Hesabı
        try:
            shape = ifcopenshell.geom.create_shape(settings, obje)
            verts = shape.geometry.verts
            x = max(verts[0::3]) - min(verts[0::3])
            y = max(verts[1::3]) - min(verts[1::3])
            z = max(verts[2::3]) - min(verts[2::3])
            hacim = x * y * z
        except:
            hacim = 1.0

        # --- AKILLI TAHMİN ALGORİTMASI ---
        mat_key = "GENEL"

        # 1. Öncelik: İsimden Sınıflandırma
        if any(k in isim for k in ["BETON", "CONCRETE", "FERTIG"]):
            mat_key = "BETON"
        elif any(k in isim for k in ["STEEL", "CELIK", "IRON"]):
            mat_key = "STEEL"
        elif any(k in isim for k in ["GLASS", "CAM"]):
            mat_key = "GLASS"

        # 2. Öncelik (AI Mantığı): Eğer isimden bulunamadıysa hacim/oran analizi
        if mat_key == "GENEL":
            # Çok ince ama geniş bir objeyse muhtemelen Cam veya Paneldir
            if (x > 1.0 and y > 1.0 and z < 0.05):
                mat_key = "GLASS"
            # Çok ağır/yoğun bir yapısal eleman gibi duruyorsa (Hacim/Tip analizi örneği)
            elif hacim < 0.1:
                mat_key = "STEEL"

            # Hassas Karbon Hesabı: Hacim * Yoğunluk * Karbon Faktörü
        info = katsayilar[mat_key]
        ağırlık = hacim * info["density"]
        obje_karbon = ağırlık * info["factor"]

        toplam_karbon += obje_karbon
        isimler_listesi.append(f"{i}-{mat_key}")
        karbon_degerleri.append(obje_karbon)

        print(f"{i:<2} | {mat_key:<6} | {hacim:>5.2f} m3 | Karbon: {obje_karbon:>8.2f} kg")

    print(f"\n🌍 TOPLAM EMİSYON: {toplam_karbon:.2f} kg CO2e")

    # Grafiği çizdir
    plt.bar(isimler_listesi, karbon_degerleri, color='darkgreen')
    plt.xticks(rotation=45)
    plt.show()


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "..", "data", "deneme.ifc")
    karbon_analizi_yap(path)