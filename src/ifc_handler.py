import ifcopenshell
import os


def model_ozetini_getir(dosya_yolu):
    # Dosyanın gerçekten orada olup olmadığını kontrol edelim
    if not os.path.exists(dosya_yolu):
        print(f"❌ Hata: '{dosya_yolu}' dizininde dosya bulunamadı!")
        return None

    try:
        model = ifcopenshell.open(dosya_yolu)
        print(f"✅ Model başarıyla yüklendi!")

        # Modeldeki her türlü fiziksel objeyi çekiyoruz
        tum_elemanlar = model.by_type("IfcProduct")

        print(f"\n--- 🕵️‍♀️ 22 OBJENİN DETAYLI LİSTESİ ---")
        print(f"Toplam Obje Sayısı: {len(tum_elemanlar)}")
        print("-" * 45)

        # Listeyi tek tek yazdıralım
        for i, obje in enumerate(tum_elemanlar, 1):
            sinif = obje.is_a()
            isim = obje.Name if obje.Name else "İsimsiz Obje"
            print(f"{i}. [Tip: {sinif:<20}] | [İsim: {isim}]")

        return model

    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")
        return None


if __name__ == "__main__":
    # Dosya yolunun doğruluğundan emin olalım
    path = "../data/deneme.ifc"
    model_ozetini_getir(path)