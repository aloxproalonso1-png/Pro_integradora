import tkinter as tk
from tkinter import messagebox
from login_controller import validar_credenciales 
from productos_viw import UserApp2


class loginapp:
    def __init__(self,root):
        self.root = root;
        self.root.title("Inicio de sesión")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

         #Encabezado
        tk.Label(root, text="Bienvenido ala barberia brabo", font=("Arial", 16, "bold")).pack(pady=16)

        #Nombre
        # Campos de texto
        tk.Label(root, text="Ingresa tu nombre de usuario:").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        #contraseña
        tk.Label(root, text="Ingresa tu contraseña:").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(root, text="Iniciar sesión", command=self.login).pack(pady=20)

    def login(self):
        usuario = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not usuario or not password:
            messagebox.showinfo("Faltan datos. Favor de ingresar usuario y contraseña")
            return

        if validar_credenciales(usuario, password):
            messagebox.showinfo("Acceso permitido", f"Bienvenido {usuario}")
            self.root.destroy()
            App2 = UserApp2(usuario)
            
        else:
            messagebox.showerror("Acceso denegado", "Tus datos son incorrectos, no se pudo ingresar.")