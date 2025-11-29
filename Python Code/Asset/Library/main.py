import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
import pygame
import sqlite3  
import os
import sys

# PyInstaller için working directory ayarı
if getattr(sys, 'frozen', False):
    # EXE olarak çalışıyorsa - PyInstaller'ın geçici klasörünü kullan
    application_path = sys._MEIPASS
else:
    # Normal Python scripti olarak çalışıyorsa (main.py Python Code/Asset/Library/ içinde)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    application_path = os.path.join(script_dir, "..", "..")

os.chdir(application_path)

# Dosya yolları için yardımcı fonksiyon
def get_asset_path(relative_path):
    """Asset dosyalarının tam yolunu döndürür"""
    if getattr(sys, 'frozen', False):
        # EXE olarak çalışıyorsa
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Normal Python olarak çalışıyorsa
        return relative_path

from quiz_data import sorular_ve_cevaplar

window = tk.Tk()
window.title("Dil yolculuğu")
width = window.winfo_screenwidth()
height = window.winfo_screenheight()
window.attributes("-fullscreen", True)  # Pencereyi tam ekran yap
window.resizable(False, False)

background_color = "#ADD8E6"
window.config(bg=background_color)
cevap_var = tk.StringVar(value="")
geri_sayim_suresi = 40  
zamanlayici = None
pygame.mixer.init()
alkis_sesi = pygame.mixer.Sound(get_asset_path("Asset/Voice/alkis_sesi.mp3"))
yanlis_sesi = pygame.mixer.Sound(get_asset_path("Asset/Voice/yanlis_cevap.mp3"))

random.shuffle(sorular_ve_cevaplar)
sorular_ve_cevaplar = sorular_ve_cevaplar[:100]  

soru_indeks = 0  # İlk sorudan başla

# Doğru ve yanlış cevap sayaçları
dogru_sayac = 0
yanlis_sayac = 0
bos_sayısı=0


image = Image.open(get_asset_path("Asset/Background/labirent.png"))
image = image.resize((800, 500))
photo = ImageTk.PhotoImage(image)

white = "f0f6f2"
canvas = tk.Canvas(window, width=805, height=500)
canvas.config(bg="white",bd=-2)  

canvas.create_image(400, 250, image=photo)

canvas.pack(side=tk.LEFT, padx=50)

canvas.create_rectangle(1,1,805,500,outline="green",width=12)

karakter_resmi = Image.open(get_asset_path("Asset/Images/karakter.png"))
karakter_resmi = karakter_resmi.resize((80, 60), Image.Resampling.LANCZOS)  # Resmi uygun boyutlandır

karakter_img = ImageTk.PhotoImage(karakter_resmi.transpose(((Image.FLIP_LEFT_RIGHT))))

timsah_resmi = Image.open(get_asset_path("Asset/Images/timsah.png"))
timsah_resmi = timsah_resmi.resize((60, 60), Image.Resampling.LANCZOS)  # Timsah resmini boyutlandır
timsah_img = ImageTk.PhotoImage(timsah_resmi)


# Karakteri canvas üzerine yerleştir
karakter = canvas.create_image(2, 15, image=karakter_img, anchor=tk.NW)

# Ödül resmi (oyun boyunca görünecek)
odul_resmi = Image.open(get_asset_path("Asset/Images/odul.png"))  # Ödül resmini yükle
odul_resmi = odul_resmi.resize((100, 100), Image.Resampling.LANCZOS)  # Resmi uygun boyutlandır
odul_img = ImageTk.PhotoImage(odul_resmi)

# Soru ve giriş alanı
frame = tk.Frame(window)
frame.config(bg=background_color)
frame.pack(side=tk.RIGHT, padx=20, pady=20)

# Çıkış butonu - sağ üstte
def cikis_yap():
    window.destroy()

cikis_butonu = tk.Button(
    window,
    text="✕ Çıkış",
    command=cikis_yap,
    font=("Arial", 14, "bold"),
    bg="#F44336",
    fg="white",
    activebackground="#D32F2F",
    activeforeground="white",
    bd=0,
    padx=15,
    pady=8,
    cursor="hand2"
)
cikis_butonu.place(x=width-120, y=10)

# ESC tuşu ile de çıkış
window.bind('<Escape>', lambda e: cikis_yap())

# Sayaçları çıkış butonu hizasında, yanlamasına (yan yana) yerleştir
# Çıkış butonu width-120 konumunda, sayaçları onun soluna diziyoruz

# Süre label'ı - solda
label_geri_sayim = tk.Label(window, text=f"Süre: {geri_sayim_suresi} sn", font=("Times New Roman", 20, "bold"), bg=background_color, fg="#FF5722")
label_geri_sayim.place(x=950, y=15)

# Doğru sayacı - sürenin yanında
label_dogru = tk.Label(window, text=f"✓ Doğru: {dogru_sayac}", font=("Times New Roman", 20, "bold"), fg="green", bg=background_color)
label_dogru.place(x=1120, y=15)

# Yanlış sayacı - doğrunun yanında
label_yanlis = tk.Label(window, text=f"✗ Yanlış: {yanlis_sayac}", font=("Times New Roman", 20, "bold"), fg="red", bg=background_color)
label_yanlis.place(x=1300, y=15)

# Boş sayacı - yanlışın yanında
label_bos = tk.Label(window, text=f"○ Boş: {bos_sayısı}", font=("Times New Roman", 20, "bold"), fg="blue", bg=background_color)
label_bos.place(x=1500, y=15) 

# Soru etiketi için bir Text alanı ekleyelim
label_soru = Text(frame, width=55, height=7, font=("Times New Roman", 20, "bold"), wrap=tk.WORD, bd=0, bg=background_color)
label_soru.pack(pady=0)  # Yukarıdan boşluk bırakmak için pady ekledik
label_soru.config(state=tk.NORMAL)



# Cevap seçimi için değişken
cevap_var = tk.StringVar(value="None")
cevap_var.set(None)

radiobuttons = []
timsah_koordinatlari = [(120, 100), (260, 217), (528, 320),(475,420),(560,220),(730,230)]  # Örnek timsah koordinatları
  #                                                         en alt      sağ üst  en sol

for index, (timsah_x, timsah_y) in enumerate(timsah_koordinatlari):
    if index == 0:  # İlk timsahı sağa döndür

        tamsah_img_donmus = ImageTk.PhotoImage(timsah_resmi.transpose((Image.FLIP_LEFT_RIGHT))) # Sağa bakacak şekilde döndür
        canvas.create_image(timsah_x, timsah_y, image=tamsah_img_donmus, anchor=tk.NW)
    else:
        canvas.create_image(timsah_x, timsah_y, image=timsah_img, anchor=tk.NW)

odul_x = 700
odul_y = 400
canvas.create_image(odul_x, odul_y, image=odul_img, anchor=tk.NW)
arry_hareket = [
    (2, 15),#start
    (2, 130),#1
    (10, 220),#2
    (80, 310),#3
    (48, 400),#4
    (250, 400),#5
    (300, 320),#6
    (360, 270),#7
    (350, 145),#9
    (270, 45),#10
    (450,45),#11
    (710,45),#12
    (710,135),#13
    (640,135),#14
    (640,320),#15
    (600,420),#16
    (odul_x,odul_y)
]

arry=[
    [(100, 15),(170, 15), (170, 120), (120, 100)],#0
    [(2,15),(100, 15),(170, 15), (170, 120), (120, 100)],#1
    [(2, 130),(2,15) , (100, 15), (170, 15), (170, 120), (120, 100)],  #2
    [(168, 310),(170, 220,),(260, 217)],#3
    [(80, 310),(168, 310),(170, 220),(260, 217)],#4
    [(48, 400),(80, 310),(168, 310),(170, 220,),(260, 217)],#5
    [(340, 350),(350, 425),(475,420)],#6
    [(435, 270),(440, 330),(528, 320)],#7
    [(360, 270),(435, 270),(440, 330),(528, 320)],#8
    [(350, 145),(360, 270),(435, 270),(440, 330),(528, 320)],#9
    [(450,175),(540,165),(528, 320)],#10
    [(450,45),(450,175),(540,165),(528, 320)],#11
    [(710,45),(450,45),(450,175),(540,165),(528, 320)],#12
    [(710,135),(710,45),(450,45),(450,175),(540,165),(528, 320)],#13
    [(720,320),(730,230)],#14
    [ (640,320),(720,320),(730,230)],#15
]

point_control =0
check_point = 0
cp2=0
hedef_koordinat=(0,0)

def sonuc_ekrani_goster(baslik, mesaj):
    """Oyun bittiğinde pencereyi kapat"""
    # Artık ekran göstermiyoruz, direkt kapatıyoruz
    window.destroy()

def karakteri_hareket_et(dogru_mu):
    global dogru_sayac, yanlis_sayac, check_point, point_control, hedef_koordinat, cp2

    if dogru_mu:
        if point_control < 1:
            # Move to the next point in the arry_hareket
            check_point += 1
            # Dizinin sonuna ulaştıysak daha fazla ilerleme
            if check_point >= len(arry_hareket):
                check_point = len(arry_hareket) - 1
                return
            
            hedef_koordinat = arry_hareket[check_point]
            animasyon_hareketi(canvas, karakter, hedef_koordinat[0], hedef_koordinat[1])
            point_control = 0
            cp2 = 0
        elif cp2 > 0:
            cp2 -= 1
            point_control -= 1
            hedef_koordinat = arry[check_point][cp2]
            animasyon_hareketi(canvas, karakter, hedef_koordinat[0], hedef_koordinat[1])
        elif point_control==1:
            cp2 = len(arry[check_point]) - 1
            hedef_koordinat = arry_hareket[check_point]
            animasyon_hareketi(canvas, karakter, hedef_koordinat[0], hedef_koordinat[1])
            cp2=0
            point_control=0

    else:
        if point_control < len(arry[check_point]):
            hedef_koordinat = arry[check_point][point_control]
            animasyon_hareketi(canvas, karakter, hedef_koordinat[0], hedef_koordinat[1])
            point_control += 1
            cp2 = point_control - 1

    print(f"check:{check_point},point:{point_control},{hedef_koordinat[0],hedef_koordinat[1]}")

def cevabi_kontrol_et():
    global dogru_sayac, yanlis_sayac, soru_indeks, bos_sayısı  # Gerekli değişkenleri tanımla
    secilen_cevap = cevap_var.get()
    
    # Kullanıcının cevap seçip seçmediğini kontrol et
    if secilen_cevap == "None":  # Kullanıcı cevap seçmediyse
        messagebox.showwarning("Uyarı", "Lütfen bir cevap seçin.")
        return

    dogru_cevap = sorular_ve_cevaplar[soru_indeks][2]  # Doğru cevabı al
    zamanlayiciyi_durdur()
    # Cevap kontrolü
    if secilen_cevap == dogru_cevap:
        dogru_sayac += 1
        label_dogru.config(text=f"✓ Doğru: {dogru_sayac}")
        alkis_sesi.play()
        messagebox.showinfo("Sonuç", "Tebrikler!🎉 Doğru Cevapladınız.")
        karakteri_hareket_et(dogru_mu=True)
        
    else:
        yanlis_sayac += 1
        label_yanlis.config(text=f"✗ Yanlış: {yanlis_sayac}")
        yanlis_sesi.play()
        messagebox.showerror("Sonuç", f"Yanlış cevap!❌ \nDoğru cevap: {dogru_cevap}")
        karakteri_hareket_et(dogru_mu=False)
    
    soru_indeks += 1
    
    if soru_indeks < len(sorular_ve_cevaplar):
        soru_goster()  
    else:
        # Tüm sorular tamamlandı
        sonuc_ekrani_goster("Tebrikler!", "Tüm soruları tamamladınız!")


def odul_yaklasti_mi(karakter_pos):
    """Karakter ödüle ulaştı mı?"""
    # Koordinatları tam sayıya çevir ve tolerans ekle (±10 piksel)
    kx, ky = int(karakter_pos[0]), int(karakter_pos[1])
    if abs(kx - odul_x) <= 10 and abs(ky - odul_y) <= 10:
        return True
    return False

def timsah_yaklasti_mi(karakter_pos):
    """Karakter bir timsahın koordinatına ulaştı mı?"""
    # Koordinatları tam sayıya çevir ve tolerans ekle (±20 piksel)
    kx, ky = int(karakter_pos[0]), int(karakter_pos[1])
    for timsah_x, timsah_y in timsah_koordinatlari:
        if abs(kx - timsah_x) <= 20 and abs(ky - timsah_y) <= 20:
            return True  
    return False

oyun_bitti_mi = False  # Oyunun bitip bitmediğini takip et

def odul_ekrani_goster():
    """Ödül ekranını gösterir"""
    # Ana pencereyi kapat
    window.destroy()
    
    # Yeni ödül penceresi oluştur
    odul_window = tk.Tk()
    odul_window.title("Ödül Ekranı")
    
    # Tam ekran ayarları - Windows kapat butonu gizli
    odul_window.attributes('-fullscreen', True)
    odul_window.attributes('-topmost', True)
    odul_window.overrideredirect(True)  # Pencere çerçevesini kaldır
    
    # Ekran boyutları
    screen_width = odul_window.winfo_screenwidth()
    screen_height = odul_window.winfo_screenheight()
    
    # Icon yükle
    try:
        icon_image = Image.open(get_asset_path("Asset/icon/game.jpg"))
        icon_photo = ImageTk.PhotoImage(icon_image)
        odul_window.iconphoto(True, icon_photo)
    except:
        pass
    
    # Ödül resmini yükle
    son_odul = Image.open(get_asset_path("Asset/Images/son_odul.jpg"))
    son_odul_photo = ImageTk.PhotoImage(son_odul)
    
    # Beyaz arka plan
    arka_plan = "#FFFFFF"
    
    # Canvas oluştur
    canvas_odul = tk.Canvas(odul_window, width=screen_width, height=screen_height, bg=arka_plan, highlightthickness=0)
    canvas_odul.pack(fill=tk.BOTH, expand=True)
    
    # Resmi ortala
    img_x = (screen_width // 2) - (son_odul_photo.width() // 2)
    img_y = (screen_height // 2) - (son_odul_photo.height() // 2) - 20
    
    # Resmi göster
    canvas_odul.create_image(img_x, img_y, image=son_odul_photo, anchor=tk.NW)
    
    # "İyi Bayramlar!" yazısı
    yazi_y = img_y + son_odul_photo.height() + 10
    
    # Gölge
    canvas_odul.create_text(
        screen_width // 2 + 3, 
        yazi_y + 3, 
        text="İyi Bayramlar!", 
        font=("Arial", 56, "bold"), 
        fill="#000000",
        anchor=tk.N
    )
    
    # Asıl yazı
    canvas_odul.create_text(
        screen_width // 2, 
        yazi_y, 
        text="İyi Bayramlar!", 
        font=("Arial", 56, "bold"), 
        fill="#FFD700",
        anchor=tk.N
    )
    
    # Çıkış butonu
    def cikis_yap():
        odul_window.destroy()
    
    cikis_butonu = tk.Button(
        odul_window, 
        text="✕ Çıkış", 
        command=cikis_yap,
        font=("Arial", 16, "bold"),
        bg="#F44336",
        fg="white",
        activebackground="#D32F2F",
        activeforeground="white",
        bd=0,
        padx=20,
        pady=10,
        cursor="hand2"
    )
    cikis_butonu.place(x=screen_width - 150, y=20)
    
    # ESC tuşu ile de çıkış
    odul_window.bind('<Escape>', lambda e: cikis_yap())
    
    odul_window.mainloop()

def odul_kontrolu_yap():
    """Her hareket sonrası ödül ve timsah kontrolü yap"""
    global dogru_sayac, yanlis_sayac, bos_sayısı, oyun_bitti_mi
    
    # Oyun zaten bittiyse bir şey yapma
    if oyun_bitti_mi:
        return
    
    # Karakterin güncel konumunu al
    x, y = canvas.coords(karakter)
    karakter_pos = (x, y)
    
    print(f"Kontrol - Karakter: ({int(x)}, {int(y)}), Ödül: ({odul_x}, {odul_y})")
    
    # Ödüle ulaştı mı?
    if odul_yaklasti_mi(karakter_pos):
        oyun_bitti_mi = True
        print("ÖDÜLE ULAŞTI!")
        # Ödül ekranını göster
        odul_ekrani_goster()
        return
    
    # Timsaha yakalandı mı?
    if timsah_yaklasti_mi(karakter_pos):
        oyun_bitti_mi = True
        print("TİMSAHA YAKALANDI!")
        sonuc_ekrani_goster("Oyun Bitti!", "Karakter bir timsaha yaklaştı!")
        return

def animasyon_hareketi(canvas, obj, hedef_x, hedef_y, adim=5):
    """Karakteri belirlenen koordinatlara adım adım hareket ettirir."""
    x, y = canvas.coords(obj)

    if abs(hedef_x - x) > adim or abs(hedef_y - y) > adim:  # Hedefe ulaşılmadıysa
        y_fark = hedef_y - y
        x_fark = hedef_x - x
        
        x_adim = adim if x_fark > 0 else -adim
        y_adim = adim if y_fark > 0 else -adim

        # Eğer x veya y farkı küçükse o eksende hareketi bitir
        if abs(x_fark) < adim:
            x_adim = x_fark
        if abs(y_fark) < adim:
            y_adim = y_fark

        # Karakteri yeni konuma adım adım taşı
        canvas.move(obj, x_adim, y_adim)
        # Bir süre sonra tekrar hareket ettir (animasyonu devam ettirmek için)
        canvas.after(50, animasyon_hareketi, canvas, obj, hedef_x, hedef_y)
    else:
        # Animasyon bitti - hedefe ulaştık
        # Karakterin son konumunu ayarla (tam hedefe koy)
        canvas.coords(obj, hedef_x, hedef_y)
        # Ödül ve timsah kontrolü yap
        canvas.after(100, odul_kontrolu_yap)

def siklari_olustur():
    global radiobuttons, cevap_var
    for rb in radiobuttons:
        rb.destroy()  # Eski şıkları temizle

    radiobuttons = []

    siklar = sorular_ve_cevaplar[soru_indeks][1]  # Şıkları al
    random.shuffle(siklar)
    for sik in siklar:
        rb = tk.Radiobutton(frame, text=sik, variable=cevap_var, value=sik, font=("Times New Roman", 20), bg=background_color)
        rb.pack(anchor='w')  # Şıkları sola yasla
        radiobuttons.append(rb)

def geri_sayim():
    global geri_sayim_suresi, zamanlayici,bos_sayısı

    # Süre dolduysa sonraki soruya geç
    if geri_sayim_suresi <= 0:
        bos_sayısı+=1
        label_bos.config(text=f"○ Boş: {bos_sayısı}")
        messagebox.showinfo("Zaman Doldu", "40 saniye içinde cevap verilmedi. Bir sonraki soruya geçiliyor.")
        sonraki_soruya_gec()
        return
    label_geri_sayim.config(text=f"Süre: {geri_sayim_suresi} sn")
    geri_sayim_suresi -= 1

    zamanlayici = window.after(1000, geri_sayim)  # 1000 ms = 1 saniye

def zamanlayiciyi_durdur():
    global zamanlayici
    if zamanlayici is not None:
        window.after_cancel(zamanlayici)  # Mevcut zamanlayıcıyı durdur

def soru_goster():
    global soru_indeks, geri_sayim_suresi,label_soru
    label_soru.delete(1.0, tk.END)  # Eski soruyu temizle
    cevap_var.set(None)
    soru_metni = sorular_ve_cevaplar[soru_indeks][0]
    
    altı_çizili_kelimeler = sorular_ve_cevaplar[soru_indeks][3] if len(sorular_ve_cevaplar[soru_indeks]) > 3 else []
    # Her kelime için altı çizgili hale getir
    for kelime in altı_çizili_kelimeler:
        soru_metni = soru_metni.replace(kelime, f"{kelime}")  # Kelimeyi vurgula

    label_soru.insert(tk.END, soru_metni)  # Yeni soruyu ekle

    # Altı çizili kelimeler için tag'leri ekle
    for kelime in altı_çizili_kelimeler:
        start_index = label_soru.search(kelime, 1.0, tk.END)
        while start_index:  # Tüm örnekleri bul
            end_index = f"{start_index} + {len(kelime)}c"
            label_soru.tag_add("underline", start_index, end_index)
            start_index = label_soru.search(kelime, end_index, tk.END)

    # Tag özelliklerini ayarla
    label_soru.tag_config("underline", underline=True)  # Altı çizgi için tag

    siklari_olustur()  # Şıkları oluştur
    geri_sayim_suresi = 40  # Her yeni soru için süreyi 40 saniyeye ayarla
    zamanlayiciyi_durdur()  # Önceki zamanlayıcıyı durdur
    geri_sayim()

def sonraki_soruya_gec():
    global soru_indeks
    soru_indeks += 1
    if soru_indeks < len(sorular_ve_cevaplar):
        soru_goster()  # Yeni soruyu göster
    else:
        # Tüm sorular tamamlandı
        sonuc_ekrani_goster("Tebrikler!", "Tüm soruları tamamladınız!")

try:
    icon_image = Image.open(get_asset_path("Asset/icon/game.jpg"))  
    icon_photo = ImageTk.PhotoImage(icon_image)
    window.iconphoto(True, icon_photo)
except:
    pass  # Icon yüklenemezse devam et

soru_goster()
print(len(sorular_ve_cevaplar))
# Cevap kontrol butonu
btn_kontrol = tk.Button(frame, text="Cevabı Kontrol Et", command=cevabi_kontrol_et, font=("Times New Roman", 30),bg="#E6A8AD", bd=-1)
btn_kontrol.pack(side=tk.BOTTOM, pady=10)

window.mainloop()
