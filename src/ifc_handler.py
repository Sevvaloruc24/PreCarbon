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
        return [], 0

    # 2. IFC ve Geometri Ayarları
    settings = ifcopenshell.geom.settings()
    try:
        model = ifcopenshell.open(dosya_yolu)
        objeler = model.by_type("IfcBuildingElementProxy")
    except Exception as e:
        print(f"❌ IFC dosyası açılamadı: {e}")
        return [], 0

    analiz_verileri = []
    isimler_listesi = []
    karbon_degerleri = []
    toplam_karbon = 0

    for i, obje in enumerate(objeler, 1):
        isim = (obje.Name or f"Obje_{i}").upper()

        # --- HACİM HESABI (Bounding Box) ---
        try:
            shape = ifcopenshell.geom.create_shape(settings, obje)
            verts = shape.geometry.verts
            x_dim = max(verts[0::3]) - min(verts[0::3])
            y_dim = max(verts[1::3]) - min(verts[1::3])
            z_dim = max(verts[2::3]) - min(verts[2::3])
            hacim = x_dim * y_dim * z_dim
        except:
            hacim = 1.0

            # --- AKILLI MALZEME TAHMİN MEKANİZMASI ---
        mat_key = "GENEL"
        if any(keyword in isim for keyword in ["BETON", "CONCRETE", "FERTIG"]):
            mat_key = "BETON"
        elif any(keyword in isim for keyword in ["STEEL", "CELIK", "IRON"]):
            mat_key = "STEEL"
        elif any(keyword in isim for keyword in ["GLASS", "CAM"]):
            mat_key = "GLASS"
        elif any(keyword in isim for keyword in ["WOOD", "AHSAP", "TIMBER"]):
            mat_key = "WOOD"

        info = katsayilar[mat_key]
        agirlik = hacim * info["density"]
        obje_karbon = agirlik * info["factor"]
        toplam_karbon += obje_karbon

        # Tablo verisi hazırla
        analiz_verileri.append({
            "No": i,
            "Obje": isim[:20],
            "Malzeme": info["name"],
            "Hacim (m3)": round(hacim, 3),
            "Karbon (kg CO2e)": round(obje_karbon, 2)
        })

        # Grafik verisi hazırla
        isimler_listesi.append(f"{i}-{mat_key}")
        karbon_degerleri.append(obje_karbon)

    # --- GRAFİK OLUŞTURMA VE İYİLEŞTİRME ---
    plt.figure(figsize=(12, 7))  # Grafik alanını genişlettik
    bars = plt.bar(isimler_listesi, karbon_degerleri, color='darkgreen', edgecolor='black')

    plt.xlabel('Objeler (No-Malzeme)', fontsize=12, fontweight='bold')
    plt.ylabel('Karbon Ayak İzi (kg CO2e)', fontsize=12, fontweight='bold')
    plt.title('PreCarbon: Obje Bazlı Karbon Analiz Raporu', fontsize=14, pad=20)

    # Eksen yazılarını düzenleme (Okunabilirliği sağlayan kritik kısım)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)

    # Izgara çizgileri ekleyelim (Opsiyonel ama şık durur)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Grafik öğelerinin birbirine girmesini önle
    plt.tight_layout()

    # Grafiği kaydet
    grafik_yolu = os.path.join(os.path.dirname(__file__), "..", "data", "karbon_grafigi.png")
    plt.savefig(grafik_yolu, dpi=150)  # Çözünürlüğü artırdık
    plt.close()

    return analiz_verileri, toplam_karbon