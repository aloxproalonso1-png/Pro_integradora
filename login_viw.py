import tkinter as tk
from tkinter import messagebox
from login_controller import validar_credenciales 
from productos_viw import UserApp2
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import numpy as np

def agregar_sombra_inferior(img, intensidad=30, desenfoque=10, opacidad=0.7):
    """
    Agrega un sombreado en la parte inferior de la imagen
    intensidad: altura de la sombra en píxeles
    desenfoque: nivel de desenfoque de la sombra
    opacidad: transparencia de la sombra (0.0 a 1.0)
    """
    # Obtener dimensiones originales
    ancho, alto = img.size
    
    # Crear nueva imagen más grande para la sombra
    nuevo_alto = alto + intensidad
    imagen_con_sombra = Image.new('RGBA', (ancho, nuevo_alto), (0, 0, 0, 0))
    
    # Crear capa de sombra
    capa_sombra = Image.new('RGBA', (ancho, intensidad), (0, 0, 0, 0))
    draw = ImageDraw.Draw(capa_sombra)
    
    # Crear gradiente lineal para la sombra
    for i in range(intensidad):
        alpha = int(opacidad * 255 * (intensidad - i) / intensidad)
        draw.line([(0, i), (ancho - 1, i)], fill=(0, 0, 0, alpha))
    
    # Aplicar desenfoque si es mayor a 0
    if desenfoque > 0:
        capa_sombra = capa_sombra.filter(ImageFilter.GaussianBlur(desenfoque))
    
    # Pegar la imagen original
    imagen_con_sombra.paste(img, (0, 0))
    
    # Pegar la sombra en la parte inferior
    imagen_con_sombra.paste(capa_sombra, (0, alto), capa_sombra)
    
    return imagen_con_sombra


class loginapp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inicio de sesión - Barbería Bravo")
        # Pantalla completa
        self.root.attributes('-fullscreen', True)
        # Alternativa si no quieres pantalla completa: self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')

        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=50, pady=(200, 0))

        # Encabezado
        tk.Label(main_frame, text="Barbería Bravo", font=("Arial", 24, "bold"), 
                bg='#f0f0f0', fg='#2c3e50').pack(pady=(200,0))
        tk.Label(main_frame, text="Sistema de Gestión", font=("Arial", 16), 
                bg='#f0f0f0', fg='#7f8c8d').pack(pady=(40, 0))

        # Frame del formulario
        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(expand=True)

        # Campos de texto
        tk.Label(form_frame, text="Usuario:", font=("Arial", 12), 
                bg='#f0f0f0').grid(row=0, column=0, padx=10, pady=15, sticky='e')
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12), width=20)
        self.username_entry.grid(row=0, column=1, padx=10, pady=15)
        self.username_entry.focus()

        tk.Label(form_frame, text="Contraseña:", font=("Arial", 12), 
                bg='#f0f0f0').grid(row=1, column=0, padx=10, pady=15, sticky='e')
        self.password_entry = tk.Entry(form_frame, show="*", font=("Arial", 12), width=20)
        self.password_entry.grid(row=1, column=1, padx=10, pady=15)

        # Frame de botones
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(pady=30)

        tk.Button(btn_frame, text="Iniciar sesión", command=self.login,
                 font=("Arial", 12, "bold"), bg='#3498db', fg='white',
                 width=15, height=2).pack(side='left', padx=10)

        # Botón para cerrar todo
        tk.Button(btn_frame, text="Salir del Sistema", command=self.salir_sistema,
                 font=("Arial", 12, "bold"), bg='#e74c3c', fg='white',
                 width=15, height=2).pack(side='left', padx=10)

        # Bind Enter para login
        self.root.bind('<Return>', lambda event: self.login())


        ancho = self.root.winfo_screenwidth()
        alto = 490

        # Cargar imagen 
        img = Image.open("ce567341-9ab4-4b0f-86b5-0d8125344e37.jpg")

        img_ancho, img_alto = img.size


        # Redimensionar TODA la pantalla a lo ancho
        img = img.resize((ancho, alto), Image.LANCZOS)

        # Convertir a RGBA si es necesario
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Agregar sombra inferior 
        img_con_sombra = agregar_sombra_inferior(img, intensidad=85, desenfoque=12, opacidad=0.8)

        # Convertir la imagen CON SOMBRA para Tkinter
        img_tk = ImageTk.PhotoImage(img_con_sombra)

        # Crear label para mostrar imagen CON SOMBRA
        label_img = tk.Label(self.root, image=img_tk)
        label_img.image = img_tk  # Mantener referencia
        label_img.place(x=0, y=0)


    def login(self):
        usuario = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not usuario or not password:
            messagebox.showwarning("Datos incompletos", "Favor de ingresar usuario y contraseña")
            return

        if validar_credenciales(usuario, password):
            messagebox.showinfo("Acceso permitido", f"Bienvenido {usuario}")
            self.root.destroy()
            App2 = UserApp2(usuario)
        else:
            messagebox.showerror("Acceso denegado", "Tus datos son incorrectos, no se pudo ingresar.")

    def salir_sistema(self):
        """Cierra completamente la aplicación"""
        if messagebox.askyesno("Salir", "¿Está seguro de que desea salir del sistema?"):
            self.root.quit()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = loginapp(root)
    root.mainloop()