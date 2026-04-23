import ifcopenshell
import os
import json


def karbon_analizi_yap(dosya_yolu):
    # 1. Katsayıları JSON'dan yükle (Hata almamak için bu kısım şart)
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "carbon_factors.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            katsayilar = data["materials"]
    except Exception as e:
        print(f"❌ JSON katsayı dosyası okunamadı veya yolu yanlış: {e}")
        return

    # 2. IFC modelini aç ve analiz et
    try:
        model = ifcopenshell.open(dosya_yolu)
        objeler = model.by_type("IfcBuildingElementProxy")

        toplam_karbon = 0
        print(f"\n--- 📊 HACİM TABANLI ANALİZ RAPORU ---")
        print(f"{'No':<3} | {'Obje İsmi':<20} | {'Hacim':<10} | {'Karbon Yükü':<15}")
        print("-" * 65)

        for i, obje in enumerate(objeler, 1):
            isim = (obje.Name or "İsimsiz").upper()

            # --- HACİM ÇEKME MANTIĞI ---
            hacim = 0.0
            # IFC hiyerarşisinde miktar (Quantity) setlerini tarıyoruz
            for rel in getattr(obje, "IsDefinedBy", []):
                if rel.is_a('IfcRelDefinesByProperties'):
                    prop_set = rel.RelatingPropertyDefinition
                    if prop_set.is_a('IfcElementQuantity'):
                        for quantity in prop_set.Quantities:
                            if quantity.is_a('IfcQuantityVolume'):
                                hacim = quantity.VolumeValue

            # Eğer hacim verisi dosyada yoksa analiz durmasın diye 1.0 varsayıyoruz
            if hacim == 0:
                hacim_notu = "(Varsayılan)"
                hacim = 1.0
            else:
                hacim_notu = "m3"

            # Malzeme belirleme ve hesaplama
            if "BETON" in isim or "BETONFERTIGTEIL" in isim:
                faktor = katsayilar["BETONFERTIGTEIL"]["factor"]
                malzeme_etiketi = "Beton"
            else:
                faktor = katsayilar["GENEL"]["factor"]
                malzeme_etiketi = "Genel"

            obje_karbon = hacim * faktor
            toplam_karbon += obje_karbon

            print(f"{i:<3} | {isim[:20]:<20} | {hacim:<6.2f} {hacim_notu:<3} | {obje_karbon:>8.2f} kg")

        print("-" * 65)
        print(f"BİNA TOPLAM KARBON AYAK İZİ: {toplam_karbon:.2f} kg CO2")

    except Exception as e:
        print(f"❌ IFC Analiz hatası: {e}")


if __name__ == "__main__":
    # Test amaçlı direkt çalıştırma yolu
    path = os.path.join(os.path.dirname(__file__), "..", "data", "deneme.ifc")
    karbon_analizi_yap(path)