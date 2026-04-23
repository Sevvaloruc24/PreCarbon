import json
import os


def katsayilari_yukle():
    # data/carbon_factors.json dosyasını okur
    json_path = os.path.join("..", "data", "carbon_factors.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def karbon_skorunu_belirle(obje_ismi):
    veriler = katsayilari_yukle()
    materyaller = veriler["materials"]

    # İsme göre katsayı seçme (Büyük/küçük harf duyarsız)
    isim = obje_ismi.upper()

    if "BETONFERTIGTEIL" in isim:
        return materyaller["BETONFERTIGTEIL"]["factor"]
    elif "STEEL" in isim or "CELIK" in isim:
        return materyaller["STEEL"]["factor"]
    else:
        return materyaller["GENEL"]["factor"]