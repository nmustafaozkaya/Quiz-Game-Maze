import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

# PyInstaller için working directory ayarı
if getattr(sys, 'frozen', False):
    # EXE olarak çalışıyorsa - PyInstaller'ın geçici klasörünü kullan
    application_path = sys._MEIPASS
else:
    # Normal Python scripti olarak çalışıyorsa (son_odul.py Python Code/Asset/Library/ içinde)
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

# Create the main window
window = tk.Tk()
window.title("Ödül Ekranı")

# Tam ekran ayarları - Windows kapat butonu gizli
window.attributes('-fullscreen', True)
window.attributes('-topmost', True)
window.overrideredirect(True)  # Pencere çerçevesini kaldır

# Get screen dimensions
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Load the icon image and set it as the window icon
try:
    icon_image = Image.open(get_asset_path("Asset/icon/game.jpg"))
    icon_photo = ImageTk.PhotoImage(icon_image)
    window.iconphoto(True, icon_photo)
except:
    pass  # Icon yüklenemezse devam et

# Load the reward image without resizing
son_odul = Image.open(get_asset_path("Asset/Images/son_odul.jpg"))
son_odul_photo = ImageTk.PhotoImage(son_odul)

# Beyaz arka plan
arka_plan = "#FFFFFF"

# Create a canvas to display the image with the specified background color
canvas = tk.Canvas(window, width=screen_width, height=screen_height, bg=arka_plan, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# Calculate image coordinates to center it (resmi ortala)
img_x = (screen_width // 2) - (son_odul_photo.width() // 2)
img_y = (screen_height // 2) - (son_odul_photo.height() // 2) - 20  # Hafif yukarıda

# Display the image on the canvas
canvas.create_image(img_x, img_y, image=son_odul_photo, anchor=tk.NW)

# Resmin altına "İyi Bayramlar" yazısı ekle (görev çubuğundan uzak)
yazi_y = img_y + son_odul_photo.height() + 15  # Resmin 15 piksel altı

# Önce gölge (siyah, hafif kaydırılmış)
canvas.create_text(
    screen_width // 2 + 3, 
    yazi_y + 3, 
    text="İyi Bayramlar!", 
    font=("Arial", 48, "bold"), 
    fill="#333333",
    anchor=tk.N
)

# Sonra asıl yazı (altın sarısı, parlak)
canvas.create_text(
    screen_width // 2, 
    yazi_y, 
    text="İyi Bayramlar!", 
    font=("Arial", 48, "bold"), 
    fill="#FFD700",
    anchor=tk.N
)

# Çıkış butonu (sağ üstte)
def cikis_yap():
    window.destroy()

cikis_butonu = tk.Button(
    window, 
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
window.bind('<Escape>', lambda e: cikis_yap())

window.mainloop()
