import os
import sys
import subprocess
from tkinter import Tk
import customtkinter as ctk # type: ignore
from PIL import Image,ImageTk # type: ignore

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("900x500")
app.title("UCMASINO")
app.resizable(False,False)
app.iconbitmap("src/assets/dado.ico")

ruta_fondo = "src/assets/img.png"
imagen = Image.open(ruta_fondo).resize((900,500))
fondo = ctk.CTkImage(light_image=imagen, dark_image=imagen,size=(900,500))
fondo_label = ctk.CTkLabel(app,text="",image= fondo)
fondo_label.place(x=0,y=0)

barra = ctk.CTkProgressBar(app, width=600,progress_color="white")
barra.place(relx=0.4,rely=0.85,anchor="center")
barra.set(0)
progreso = 0.0

# Nueva etiqueta de "Cargando..."
cargando_textos = ["Cargando.", "Cargando..", "Cargando..."]
cargando_index = 0
cargando_label = ctk.CTkLabel(app, text=cargando_textos[0], font=("Arial", 18, "bold"), text_color="white", bg_color="#0e0e0e")  
cargando_label.place(relx=0.10, rely=0.78, anchor="w") 


def animar_cargando():
    global cargando_index
    cargando_index = (cargando_index + 1) % len(cargando_textos)
    cargando_label.configure(text=cargando_textos[cargando_index])
    app.after(400, animar_cargando)

def cargar():
    global progreso
    if progreso < 1:
        progreso += 0.01
        barra.set(progreso)
        app.after(20, cargar)  
    else:
        app.destroy()
        subprocess.Popen([sys.executable, os.path.abspath("src/menu/menu.py")])

animar_cargando()
cargar()
app.mainloop()
