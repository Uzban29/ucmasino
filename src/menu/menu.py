import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from src.db.database import add_user, verify_user, get_user
from src.game.dice import main as open_dado

BG_COLOR = "#0e0e0e"
WINE     = "#E53053"
ROSE     = "#FFC0CB"
FONT_PATH = "src/assetes/BigBlue.ttf"
DEFAULT_FONT = (FONT_PATH, 16, "bold")

# --- GIF animado para login/registro ---
class AnimatedGIF(ctk.CTkLabel):
    def __init__(self, master, path, delay=100):
        im = Image.open(path)
        self.frames = []
        try:
            for frame in range(0, im.n_frames):
                im.seek(frame)
                frame_image = ImageTk.PhotoImage(im.copy())
                self.frames.append(frame_image)
        except Exception:
            self.frames.append(ImageTk.PhotoImage(im))
        super().__init__(master, image=self.frames[0], text="")
        self.delay = delay
        self.idx = 0
        self.after(self.delay, self.play)

    def play(self):
        self.idx = (self.idx + 1) % len(self.frames)
        self.configure(image=self.frames[self.idx])
        self.after(self.delay, self.play)

def es_correo_valido(correo):
    return "@" in correo and "." in correo

# --- Registro de usuario ---
def OpenRegister():
    ctk.set_appearance_mode("dark")
    w = ctk.CTk()
    w.geometry("900x600")
    w.title("Registro - UCMASINO")
    w.configure(fg_color=BG_COLOR)
    w.resizable(False, False)

    def volver_login():
        w.destroy()
        LoginMain()

    # --- Contenedor principal ---
    main_container = ctk.CTkFrame(w, fg_color=BG_COLOR)
    main_container.pack(fill="both", expand=True)

    # --- Panel Izquierdo (GIF/Logo) ---
    left_frame = ctk.CTkFrame(main_container, width=450, height=600, fg_color=WINE)
    left_frame.pack(side="left", fill="both")
    left_frame.pack_propagate(False)
    gif_path = os.path.join("src/config/relax.gif")
    if os.path.exists(gif_path):
        gif_label = AnimatedGIF(left_frame, gif_path, delay=100)
        gif_label.pack(expand=True)
    else:
        ctk.CTkLabel(left_frame, text="UCMASINO", text_color=ROSE, font=(FONT_PATH, 32, "bold")).pack(expand=True)

    # --- Panel Derecho (Formulario) ---
    right_frame = ctk.CTkFrame(main_container, width=450, height=600, fg_color=BG_COLOR)
    right_frame.pack(side="right", fill="both")
    right_frame.pack_propagate(False)

    formulario = ctk.CTkFrame(right_frame, fg_color="transparent")
    formulario.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(formulario, text="Registro de Usuario", text_color=ROSE, font=(FONT_PATH, 24, "bold")).pack(pady=(0, 20))
    entry_usuario = ctk.CTkEntry(formulario, placeholder_text="Usuario", width=300, font=DEFAULT_FONT)
    entry_usuario.pack(pady=5)
    entry_contrasena = ctk.CTkEntry(formulario, placeholder_text="Contraseña", width=300, show="•", font=DEFAULT_FONT)
    entry_contrasena.pack(pady=5)
    entry_confirmar = ctk.CTkEntry(formulario, placeholder_text="Confirmar Contraseña", width=300, show="•", font=DEFAULT_FONT)
    entry_confirmar.pack(pady=5)
    entry_correo = ctk.CTkEntry(formulario, placeholder_text="Correo", width=300, font=DEFAULT_FONT)
    entry_correo.pack(pady=5)
    entry_nombre = ctk.CTkEntry(formulario, placeholder_text="Nombre", width=300, font=DEFAULT_FONT)
    entry_nombre.pack(pady=5)
    entry_edad = ctk.CTkEntry(formulario, placeholder_text="Edad", width=300, font=DEFAULT_FONT)
    entry_edad.pack(pady=5)

    def registrar():
        usuario = entry_usuario.get().strip()
        contrasena = entry_contrasena.get().strip()
        confirmar = entry_confirmar.get().strip()
        correo = entry_correo.get().strip()
        nombre = entry_nombre.get().strip()
        edad = entry_edad.get().strip()

        # Validaciones
        if not (usuario and contrasena and confirmar and correo and nombre and edad):
            messagebox.showwarning("Campos incompletos", "Por favor, completa todos los campos.")
            return
        if contrasena != confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        if not es_correo_valido(correo):
            messagebox.showerror("Correo inválido", "El correo debe contener '@' y '.'")
            return
        try:
            edad_int = int(edad)
            if edad_int < 18:
                messagebox.showerror("Edad no permitida", "Debes tener al menos 18 años para registrarte.")
                return
        except ValueError:
            messagebox.showerror("Edad inválida", "Por favor, ingresa una edad válida.")
            return

        try:
            ok, msg = add_user(usuario, contrasena, correo, nombre, edad)
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
            return

        if ok:
            messagebox.showinfo("Registro exitoso", "¡Usuario registrado correctamente! Inicia sesión.")
            w.destroy()
            LoginMain()
        else:
            messagebox.showerror("Error", msg)

    ctk.CTkButton(formulario, text="Registrarse", width=300, fg_color=WINE, hover_color=ROSE, corner_radius=15, command=registrar, font=DEFAULT_FONT).pack(pady=10)
    ctk.CTkButton(formulario, text="Volver", fg_color=WINE, corner_radius=15, hover_color=ROSE, width=100, command=volver_login, font=DEFAULT_FONT).pack(pady=5)
    ctk.CTkButton(formulario, text="Salir", fg_color=WINE, corner_radius=15, hover_color=ROSE, width=100, command=w.destroy, font=DEFAULT_FONT).pack(pady=5)

    entry_usuario.focus()
    w.mainloop()

# --- Login ---
def LoginMain():
    ctk.set_appearance_mode("dark")
    w = ctk.CTk()
    w.geometry("900x600")
    w.title("Login - UCMASINO")
    w.configure(fg_color=BG_COLOR)
    w.resizable(False, False)
    w.iconbitmap("src/assets/dado.ico")
    
    def open_register():
        w.destroy()
        OpenRegister()

    main_container = ctk.CTkFrame(w, fg_color=BG_COLOR)
    main_container.pack(fill="both", expand=True)

    # --- Panel Izquierdo (GIF/Logo) ---
    left_frame = ctk.CTkFrame(main_container, width=450, height=600, fg_color=WINE)
    left_frame.pack(side="left", fill="both")
    left_frame.pack_propagate(False)
    gif_path = os.path.join("src/config/relax.gif")
    if os.path.exists(gif_path):
        gif_label = AnimatedGIF(left_frame, gif_path, delay=100)
        gif_label.pack(expand=True)
    else:
        ctk.CTkLabel(left_frame, text="UCMASINO", text_color=ROSE, font=(FONT_PATH, 32, "bold")).pack(expand=True)

    # --- Panel Derecho (Formulario) ---
    right_frame = ctk.CTkFrame(main_container, width=450, height=600, fg_color=BG_COLOR)
    right_frame.pack(side="right", fill="both")
    right_frame.pack_propagate(False)

    formulario = ctk.CTkFrame(right_frame, fg_color="transparent")
    formulario.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(formulario, text="Iniciar Sesión", text_color=ROSE, font=(FONT_PATH, 24, "bold")).pack(pady=(0, 20))
    user_entry = ctk.CTkEntry(formulario, placeholder_text="Usuario", width=300, font=DEFAULT_FONT)
    user_entry.pack(pady=10)

    pass_visible = [False]
    def toggle_password():
        if pass_visible[0]:
            passwd_entry.configure(show="•")
            toggle_btn.configure(text="👁")
        else:
            passwd_entry.configure(show="")
            toggle_btn.configure(text="🚫")
        pass_visible[0] = not pass_visible[0]

    passwd_frame = ctk.CTkFrame(formulario, fg_color="transparent")
    passwd_frame.pack(pady=10)

    passwd_entry = ctk.CTkEntry(passwd_frame, placeholder_text="Contraseña", width=260, show="•", font=DEFAULT_FONT)
    passwd_entry.pack(side="left", padx=(0, 5))

    toggle_btn = ctk.CTkButton(passwd_frame, text="👁", width=30, height=30, command=toggle_password, hover_color=ROSE, fg_color=WINE)
    toggle_btn.pack(side="left")

    def login_action():
        usuario = user_entry.get().strip()
        contrasena = passwd_entry.get().strip()
        if not usuario or not contrasena:
            messagebox.showwarning("Campos vacíos", "Por favor, ingresa usuario y contraseña.")
            return
        try:
            ok = verify_user(usuario, contrasena)
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
            return
        if ok:
            w.destroy()
            open_dado(usuario)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    ctk.CTkButton(formulario, text="Iniciar sesión", width=300, fg_color=WINE, hover_color=ROSE, corner_radius=15,  command=login_action, font=DEFAULT_FONT).pack(pady=20)
    ctk.CTkButton(formulario, text="Registrar", width=300, fg_color=WINE, hover_color=ROSE, corner_radius=15,  command=open_register, font=DEFAULT_FONT).pack(pady=10)
    ctk.CTkButton(formulario, text="Salir", fg_color=WINE, corner_radius=15, hover_color=ROSE, width=100, command=w.destroy, font=DEFAULT_FONT).pack(pady=10)

    user_entry.focus()
    w.mainloop()


if __name__ == "__main__":
    LoginMain()

