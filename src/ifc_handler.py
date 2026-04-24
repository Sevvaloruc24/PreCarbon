import ifcopenshell
import ifcopenshell.geom
import os
import json
import matplotlib.pyplot as plt


def karbon_analizi_yap(dosya_yolu):
    # 1. Genişletilmiş Katsayıları JSON'dan Yükle
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

        # --- HACİM HESABI ---
        try:
            shape = ifcopenshell.geom.create_shape(settings, obje)
            verts = shape.geometry.verts
            hacim = (max(verts[0::3]) - min(verts[0::3])) * \
                    (max(verts[1::3]) - min(verts[1::3])) * \
                    (max(verts[2::3]) - min(verts[2::3]))
        except:
            hacim = 1.0

            # --- 🧠 3. AŞAMA: DERİNLEŞTİRİLMİŞ MALZEME TAHMİN MEKANİZMASI ---
        mat_key = "GENEL"

        # Beton Detaylandırma
        if any(k in isim for k in ["BETON", "CONCRETE", "FERTIG"]):
            if any(k in isim for k in ["RECYCLED", "GERI", "DONUSUM"]):
                mat_key = "BETON_GERIDONUSUM"
            else:
                mat_key = "BETON_STANDART"

        # Çelik Detaylandırma
        elif any(k in isim for k in ["STEEL", "CELIK", "IRON"]):
            if any(k in isim for k in ["REBAR", "DONATI", "HASIR", "BAR"]):
                mat_key = "STEEL_REBAR"
            else:
                mat_key = "STEEL_SECTION"

        # Cam Detaylandırma
        elif any(k in isim for k in ["GLASS", "CAM"]):
            mat_key = "GLASS_TRIPLE"

        # Ahşap Detaylandırma
        elif any(k in isim for k in ["WOOD", "AHSAP", "TIMBER"]):
            mat_key = "WOOD_SOFTWOOD"

        # Veri çekme ve Hesaplama
        info = katsayilar.get(mat_key, katsayilar["GENEL"])
        agirlik = hacim * info["density"]
        obje_karbon = agirlik * info["factor"]
        toplam_karbon += obje_karbon

        # Tablo verisi (Genişletilmiş Metrikler)
        analiz_verileri.append({
            "No": i,
            "Obje": isim[:20],
            "Tahmin Edilen Malzeme": info["name"],
            "Hacim (m3)": round(hacim, 3),
            "Yoğunluk (kg/m3)": info["density"],
            "Karbon Yükü (kg CO2e)": round(obje_karbon, 2)
        })

        isimler_listesi.append(f"{i}-{mat_key[:5]}")
        karbon_degerleri.append(obje_karbon)

    # --- GRAFİK OLUŞTURMA ---
    plt.figure(figsize=(12, 7))
    plt.bar(isimler_listesi, karbon_degerleri, color='darkgreen', edgecolor='black')
    plt.xlabel('Objeler (ID-Tip)', fontsize=12)
    plt.ylabel('Karbon Ayak İzi (kg CO2e)', fontsize=12)
    plt.title('PreCarbon: Derinlemesine Malzeme Analiz Raporu', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    grafik_yolu = os.path.join(os.path.dirname(__file__), "..", "data", "karbon_grafigi.png")
    plt.savefig(grafik_yolu, dpi=150)
    plt.close()

    return analiz_verileri, toplam_karbon