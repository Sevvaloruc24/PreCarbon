import ifcopenshell


def model_ozetini_getir(dosya_yolu):
    try:
        model = ifcopenshell.open(dosya_yolu)
        print(f"✅ Model başarıyla yüklendi!")

        # .by_type() fonksiyonu bazen alt sınıfları kapsamaz.
        # Bu yüzden daha geniş bir arama yapıyoruz:
        duvarlar = model.by_type("IfcWall") + model.by_type("IfcWallStandardCase")
        dosemeler = model.by_type("IfcSlab")
        kolonlar = model.by_type("IfcColumn")
        tum_elemanlar = model.by_type("IfcProduct")  # Modeldeki her türlü fiziksel obje

        print(f"--- Bina Özeti ---")
        print(f"Toplam Duvar Sayısı: {len(duvarlar)}")
        print(f"Toplam Döşeme Sayısı: {len(dosemeler)}")
        print(f"Toplam Kolon Sayısı: {len(kolonlar)}")
        print(f"Modeldeki Toplam Obje Sayısı: {len(tum_elemanlar)}")

        return model

    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")
        return None


if __name__ == "__main__":
    path = "../data/deneme.ifc"
    model_ozetini_getir(path)