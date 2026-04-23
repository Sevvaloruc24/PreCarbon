import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# src klasöründeki fonksiyonu içeri aktar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ifc_handler import karbon_analizi_yap


def dosya_sec_ve_baslat():
    # Dosya seçme penceresini aç
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle, sadece dosya seçiciyi göster

    file_path = filedialog.askopenfilename(
        title="Analiz Edilecek IFC Dosyasını Seçin",
        filetypes=[("IFC Files", "*.ifc"), ("All Files", "*.*")]
    )

    if file_path:
        try:
            print(f"🚀 Seçilen dosya üzerinde analiz başlatılıyor: {file_path}")
            karbon_analizi_yap(file_path)
            messagebox.showinfo("Başarılı", "Analiz tamamlandı ve grafik oluşturuldu!")
        except Exception as e:
            messagebox.showerror("Hata", f"Analiz sırasında bir sorun oluştu:\n{e}")
    else:
        print("⚠️ Herhangi bir dosya seçilmedi.")


if __name__ == "__main__":
    dosya_sec_ve_baslat()