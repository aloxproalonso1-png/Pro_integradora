import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from usuarios_controller import (
    obtener_usuarios, 
    obtener_usuario_por_id, 
    agregar_usuario, 
    actualizar_usuario, 
    eliminar_usuario,
    buscar_usuarios,
    obtener_roles_disponibles
)

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")  # "dark", "light", "system"
ctk.set_default_color_theme("blue")

def cargar_imagen(ruta, tamaño=(80, 80)):
    """Carga y redimensiona una imagen para CustomTkinter"""
    try:
        img = Image.open(ruta)
        img = img.resize(tamaño, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=tamaño)
    except Exception as e:
        print(f"Error al cargar imagen: {e}")
        return None

class UsuariosView:
    def __init__(self, root, usuario_actual=None, user_app_ref=None):
        self.root = root
        self.usuario_actual = usuario_actual
        self.user_app_ref = user_app_ref  # Referencia a la app principal
        
        self.root.title("👥 Gestión de Usuarios - Barbería Bravo")
        
        # CONFIGURAR VENTANA MÁS GRANDE
        self.root.geometry("1400x850")  # Tamaño aumentado
        
        # Centrar ventana
        self.root.update_idletasks()
        ancho = 1400
        alto = 850
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # Hacer que la ventana sea redimensionable
        self.root.resizable(True, True)
        
        # Variables
        self.buscar_var = tk.StringVar()
        self.menu_abierto = False
        self.logo = cargar_imagen("c9141f85-d013-448a-aea0-2201255befd4.jpg", tamaño=(70, 70))  # Logo más grande
        
        self.crear_interfaz()
        self.actualizar_lista()
        self.root.focus_set()
    
    def crear_interfaz(self):
        # ============================================
        # 1. HEADER SUPERIOR (MÁS GRANDE)
        # ============================================
        header_frame = ctk.CTkFrame(self.root, height=100, corner_radius=0, fg_color="#1a1a1a")  # Más alto
        header_frame.pack(fill='x', side='top')
        
        # Logo y título (más grande)
        if self.logo:
            img_label = ctk.CTkLabel(header_frame, image=self.logo, text="", fg_color="#1a1a1a")
            img_label.pack(side='left', padx=(30, 20), pady=15)  # Más padding
        
        ctk.CTkLabel(header_frame, 
                     text="👥 GESTIÓN DE USUARIOS - BARBERÍA BRAVO", 
                     font=ctk.CTkFont(family="Arial", size=24, weight="bold"),  # Fuente más grande
                     text_color="white").pack(side='left', padx=10, pady=15)
        
        # Información del usuario actual
        if self.usuario_actual:
            user_info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            user_info_frame.pack(side='right', padx=30, pady=15)
            
            ctk.CTkLabel(user_info_frame, 
                         text=f"👤 USUARIO: {self.usuario_actual}", 
                         font=ctk.CTkFont(size=13, weight="bold"),  # Fuente más grande
                         text_color="#cccccc").pack(side='top', anchor='e')
        
        # Botón hamburguesa (más grande)
        self.btn_hamburguesa = ctk.CTkButton(header_frame, 
                                            text="☰ MENÚ PRINCIPAL", 
                                            width=150,  # Más ancho
                                            height=40,  # Más alto
                                            command=self.toggle_menu,
                                            fg_color="#3498db",
                                            hover_color="#2980b9",
                                            font=ctk.CTkFont(size=13, weight="bold"))  # Fuente más grande
        self.btn_hamburguesa.pack(side='right', padx=(0, 20), pady=15)
        
        # ============================================
        # 2. PANEL DE MENÚ LATERAL (MÁS ANCHO)
        # ============================================
        self.panel_menu = ctk.CTkFrame(self.root, width=280, corner_radius=0, fg_color="#2c3e50")  # Más ancho
        self.panel_menu.place(x=-280, y=100, relheight=1)
        
        opciones = [
            ("↶ VOLVER AL PUNTO DE VENTA", self.volver_punto_venta, True),
            ("➕ AGREGAR NUEVO USUARIO", self.mostrar_agregar_usuario, True),
            ("🔄 ACTUALIZAR LISTA", self.actualizar_lista, True),
            ("🔍 BUSCAR USUARIOS", self.focus_buscar, True),
            ("📊 ESTADÍSTICAS", self.mostrar_estadisticas, True),
            ("❌ CERRAR VENTANA", self.root.destroy, True)
        ]

        # Crear botones del menú (más grandes)
        for i, (texto, comando, visible) in enumerate(opciones):
            if visible:
                btn = ctk.CTkButton(self.panel_menu, text=texto,
                                  command=lambda cmd=comando: [cmd(), self.toggle_menu()],
                                  fg_color="transparent",
                                  hover_color="#34495e",
                                  text_color="white",
                                  font=ctk.CTkFont(family="Arial", size=13),  # Fuente más grande
                                  anchor='w',
                                  height=50,  # Más alto
                                  width=260)  # Más ancho
                btn.place(x=10, y=30 + i*55)  # Más espacio entre botones
        
        # ============================================
        # 3. CONTENIDO PRINCIPAL (CON MÁS ESPACIO)
        # ============================================
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)  # Más padding
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # ============================================
        # 4. BARRA DE BÚSQUEDA (MÁS GRANDE)
        # ============================================
        buscar_frame = ctk.CTkFrame(main_container, corner_radius=12)  # Más redondeado
        buscar_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(0, 15))
        buscar_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(buscar_frame, 
                     text="🔍 BUSCAR USUARIOS:", 
                     font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=15)  # Fuente más grande
        
        self.entry_buscar = ctk.CTkEntry(buscar_frame,
                                       textvariable=self.buscar_var,
                                       placeholder_text="Ingrese nombre de usuario o rol...",
                                       font=ctk.CTkFont(size=13),  # Fuente más grande
                                       height=40,  # Más alto
                                       width=300)  # Más ancho
        self.entry_buscar.grid(row=0, column=1, padx=15, pady=15, sticky='ew')
        
        btn_buscar = ctk.CTkButton(buscar_frame,
                                  text="🔍 BUSCAR",
                                  command=self.buscar_usuarios,
                                  fg_color="#3498db",
                                  hover_color="#2980b9",
                                  width=140,  # Más ancho
                                  height=40,  # Más alto
                                  font=ctk.CTkFont(size=13, weight="bold"))
        btn_buscar.grid(row=0, column=2, padx=15, pady=15)
        
        btn_mostrar = ctk.CTkButton(buscar_frame,
                                   text="🔄 MOSTRAR TODOS",
                                   command=self.actualizar_lista,
                                   fg_color="#f39c12",
                                   hover_color="#d68910",
                                   width=160,  # Más ancho
                                   height=40,  # Más alto
                                   font=ctk.CTkFont(size=13, weight="bold"))
        btn_mostrar.grid(row=0, column=3, padx=15, pady=15)
        
        # ============================================
        # 5. LISTA DE USUARIOS (TREEVIEW MÁS GRANDE)
        # ============================================
        tree_frame = ctk.CTkFrame(main_container, corner_radius=12)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 15))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Configurar estilo del Treeview (más grande)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", 
                       font=('Arial', 12, 'bold'),  # Fuente más grande
                       background='#34495e', 
                       foreground='white',
                       padding=8)  # Más padding
        style.configure("Treeview", 
                       font=('Arial', 11),  # Fuente más grande
                       rowheight=35,  # Filas más altas
                       background='white',
                       fieldbackground='white',
                       foreground='black')
        style.map('Treeview', 
                 background=[('selected', '#3498db')])
        
        # Crear Treeview (más grande)
        columns = ('ID', 'USUARIO', 'ROL', 'FECHA REGISTRO')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=18)  # Más alto
        
        # Configurar columnas (más anchas)
        column_configs = [
            ('ID', 80, 'center'),        # Más ancho
            ('USUARIO', 250, 'w'),       # Más ancho
            ('ROL', 180, 'center'),      # Más ancho
            ('FECHA REGISTRO', 220, 'center')  # Más ancho
        ]
        
        for col, width, anchor in column_configs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars (más visibles)
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Scrollbar horizontal para columnas anchas
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, columnspan=2, sticky='ew')
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind double click para editar
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # ============================================
        # 6. BOTONES DE ACCIÓN (MÁS GRANDES)
        # ============================================
        action_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 10))
        
        # Definir botones principales (más grandes)
        botones_principales = [
            ("➕ AGREGAR USUARIO", self.mostrar_agregar_usuario, '#3498db'),
            ("✏️ EDITAR SELECCIONADO", self.mostrar_editar_usuario, '#2ecc71'),
            ("🗑️ ELIMINAR SELECCIONADO", self.mostrar_eliminar_usuario, '#e74c3c'),
            ("🔄 ACTUALIZAR LISTA", self.actualizar_lista, '#9b59b6'),
            ("📊 ESTADÍSTICAS", self.mostrar_estadisticas, '#f39c12')
        ]
        
        for i, (texto, comando, color) in enumerate(botones_principales):
            btn = ctk.CTkButton(action_frame,
                              text=texto,
                              command=comando,
                              fg_color=color,
                              hover_color=self.oscurecer_color(color),
                              height=45,  # Más alto
                              width=180,  # Más ancho
                              font=ctk.CTkFont(size=13, weight="bold"),  # Fuente más grande
                              corner_radius=8)  # Más redondeado
            btn.grid(row=0, column=i, padx=8, pady=8)
            action_frame.grid_columnconfigure(i, weight=1)
    
    def oscurecer_color(self, color):
        """Oscurece un color para el efecto hover"""
        colores = {
            '#3498db': '#2980b9',
            '#2ecc71': '#27ae60',
            '#e74c3c': '#c0392b',
            '#9b59b6': '#8e44ad',
            '#f39c12': '#d68910'
        }
        return colores.get(color, color)
    
    def toggle_menu(self):
        """Alterna el estado del menú lateral"""
        if not self.menu_abierto:
            self.panel_menu.place(x=0, y=100)
            self.panel_menu.lift()
            self.menu_abierto = True
        else:
            self.panel_menu.place(x=-280, y=100)
            self.menu_abierto = False
    
    def focus_buscar(self):
        """Coloca el foco en el campo de búsqueda"""
        self.entry_buscar.focus_set()
        self.toggle_menu()
    
    # ============================================
    # MÉTODOS DE GESTIÓN DE USUARIOS
    # ============================================
    
    def actualizar_lista(self):
        """Actualiza la lista de usuarios"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        usuarios = obtener_usuarios()
        if usuarios:
            for usuario in usuarios:
                fecha_formateada = usuario['fecha'].strftime("%Y-%m-%d %H:%M") if usuario['fecha'] else "N/A"
                
                self.tree.insert('', tk.END, values=(
                    usuario['Id'],
                    usuario['Usuario'],
                    usuario['Rol'],
                    fecha_formateada
                ))
    
    def buscar_usuarios(self):
        """Busca usuarios según el término ingresado"""
        termino = self.buscar_var.get().strip()
        if not termino:
            self.actualizar_lista()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        usuarios = buscar_usuarios(termino)
        if usuarios:
            for usuario in usuarios:
                fecha_formateada = usuario['fecha'].strftime("%Y-%m-%d %H:%M") if usuario['fecha'] else "N/A"
                
                self.tree.insert('', tk.END, values=(
                    usuario['Id'],
                    usuario['Usuario'],
                    usuario['Rol'],
                    fecha_formateada
                ))
    
    def on_double_click(self, event):
        """Al hacer doble click en un usuario, lo edita"""
        self.mostrar_editar_usuario()
    
    # ============================================
    # VENTANAS DE FORMULARIO (CORREGIDAS Y MÁS GRANDES)
    # ============================================
    
    def mostrar_agregar_usuario(self):
        """Ventana para agregar nuevo usuario (CORREGIDA)"""
        self.ventana_agregar = ctk.CTkToplevel(self.root)
        self.ventana_agregar.title("➕ AGREGAR NUEVO USUARIO")
        self.ventana_agregar.geometry("650x600")  # Ventana más grande
        self.ventana_agregar.transient(self.root)
        self.ventana_agregar.grab_set()
        
        self.centrar_ventana(self.ventana_agregar, 650, 600)
        self.crear_formulario_usuario(self.ventana_agregar, None, modo='agregar')
    
    def mostrar_editar_usuario(self):
        """Ventana para editar usuario seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "⚠️ Por favor seleccione un usuario para editar")
            return
        
        item = self.tree.item(seleccion[0])
        id_usuario = item['values'][0]
        
        usuario = obtener_usuario_por_id(id_usuario)
        if not usuario:
            messagebox.showerror("Error", "❌ No se pudo obtener la información del usuario")
            return
        
        self.ventana_editar = ctk.CTkToplevel(self.root)
        self.ventana_editar.title(f"✏️ EDITAR USUARIO: {usuario['Usuario']}")
        self.ventana_editar.geometry("650x700")  # Ventana más grande
        self.ventana_editar.transient(self.root)
        self.ventana_editar.grab_set()
        
        self.centrar_ventana(self.ventana_editar, 650, 700)
        self.crear_formulario_usuario(self.ventana_editar, usuario, modo='editar')
    
    def crear_formulario_usuario(self, ventana, usuario=None, modo='agregar'):
        """Crea el formulario para agregar/editar usuarios (VERSIÓN CORREGIDA)"""
        frame = ctk.CTkFrame(ventana, corner_radius=12)
        frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # CONFIGURAR GRID DEL FRAME PRINCIPAL
        frame.grid_columnconfigure(1, weight=1)  # Permitir que la columna 1 se expanda
        
        # Título
        if modo == 'editar':
            titulo = f"✏️ EDITAR USUARIO: {usuario['Usuario']}"
        else:
            titulo = "➕ AGREGAR NUEVO USUARIO"
            
        ctk.CTkLabel(frame, 
                     text=titulo,
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#2c3e50").grid(row=0, column=0, columnspan=2, padx=15, pady=(0, 30), sticky='w')
        
        # Campos del formulario
        self.entries = {}
        current_row = 1
        
        # Campo Usuario
        ctk.CTkLabel(frame, 
                    text="👤 Nombre de Usuario:",
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=current_row, column=0, padx=15, pady=15, sticky='w')
        
        entry_usuario = ctk.CTkEntry(frame,
                                   placeholder_text="Ingrese nombre de usuario",
                                   font=ctk.CTkFont(size=13),
                                   height=40,
                                   width=350)  # Más ancho
        if usuario:
            entry_usuario.insert(0, usuario['Usuario'])
        entry_usuario.grid(row=current_row, column=1, padx=15, pady=15, sticky='ew')
        self.entries['usuario'] = entry_usuario
        
        current_row += 1
        
        # Campo Rol
        ctk.CTkLabel(frame, 
                    text="👑 Rol del Usuario:",
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=current_row, column=0, padx=15, pady=15, sticky='w')
        
        roles = obtener_roles_disponibles()
        combo_rol = ctk.CTkComboBox(frame,
                                  values=roles,
                                  font=ctk.CTkFont(size=13),
                                  height=40,
                                  width=350)
        if usuario:
            combo_rol.set(usuario['Rol'])
        else:
            combo_rol.set("vendedor")  # Valor por defecto
        combo_rol.grid(row=current_row, column=1, padx=15, pady=15, sticky='w')
        self.entries['rol'] = combo_rol
        
        current_row += 1
        
        # Campos de contraseña (diferentes para agregar y editar)
        if modo == 'agregar':
            # Para nuevo usuario - campos de contraseña siempre visibles
            
            ctk.CTkLabel(frame, 
                        text="🔒 Contraseña:",
                        font=ctk.CTkFont(size=14, weight="bold")).grid(row=current_row, column=0, padx=15, pady=15, sticky='w')
            
            self.entry_password = ctk.CTkEntry(frame,
                                             show="*",
                                             placeholder_text="Ingrese contraseña (mínimo 4 caracteres)",
                                             font=ctk.CTkFont(size=13),
                                             height=40,
                                             width=350)
            self.entry_password.grid(row=current_row, column=1, padx=15, pady=15, sticky='ew')
            
            current_row += 1
            
            ctk.CTkLabel(frame, 
                        text="🔒 Confirmar Contraseña:",
                        font=ctk.CTkFont(size=14, weight="bold")).grid(row=current_row, column=0, padx=15, pady=15, sticky='w')
            
            self.entry_confirmar = ctk.CTkEntry(frame,
                                               show="*",
                                               placeholder_text="Confirme la contraseña",
                                               font=ctk.CTkFont(size=13),
                                               height=40,
                                               width=350)
            self.entry_confirmar.grid(row=current_row, column=1, padx=15, pady=15, sticky='ew')
            
            current_row += 1
            
        else:
            # Para editar usuario - checkbox para cambiar contraseña
            
            self.cambiar_password_var = ctk.BooleanVar(value=False)
            chk_cambiar = ctk.CTkCheckBox(frame,
                                         text="🔓 CAMBIAR CONTRASEÑA",
                                         variable=self.cambiar_password_var,
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         command=lambda: self.toggle_campos_password(frame, current_row))
            chk_cambiar.grid(row=current_row, column=0, columnspan=2, padx=15, pady=20, sticky='w')
            
            current_row += 1
            
            # Frame para campos de contraseña (inicialmente oculto)
            self.frame_password = ctk.CTkFrame(frame, fg_color="transparent")
            self.frame_password.grid(row=current_row, column=0, columnspan=2, padx=15, pady=10, sticky='ew')
            self.frame_password.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(self.frame_password, 
                        text="🔒 Nueva Contraseña:",
                        font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
            
            self.entry_password = ctk.CTkEntry(self.frame_password,
                                             show="*",
                                             placeholder_text="Ingrese nueva contraseña",
                                             font=ctk.CTkFont(size=13),
                                             height=35,
                                             width=350,
                                             state='disabled')
            self.entry_password.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
            
            ctk.CTkLabel(self.frame_password, 
                        text="🔒 Confirmar Contraseña:",
                        font=ctk.CTkFont(size=13)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
            
            self.entry_confirmar = ctk.CTkEntry(self.frame_password,
                                               show="*",
                                               placeholder_text="Confirme la nueva contraseña",
                                               font=ctk.CTkFont(size=13),
                                               height=35,
                                               width=350,
                                               state='disabled')
            self.entry_confirmar.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
            
            # Inicialmente ocultar campos de contraseña
            self.frame_password.grid_remove()
            current_row += 2
        
        # Frame de botones
        botones_frame = ctk.CTkFrame(frame, fg_color="transparent")
        botones_frame.grid(row=current_row, column=0, columnspan=2, pady=(30, 0))
        
        if modo == 'editar':
            btn_guardar = ctk.CTkButton(botones_frame,
                                      text="💾 GUARDAR CAMBIOS",
                                      command=lambda: self.guardar_edicion_usuario(
                                          usuario['Id'],
                                          self.entries['usuario'].get(),
                                          self.entries['rol'].get(),
                                          self.cambiar_password_var.get(),
                                          self.entry_password.get() if hasattr(self, 'entry_password') else "",
                                          self.entry_confirmar.get() if hasattr(self, 'entry_confirmar') else ""
                                      ),
                                      fg_color="#3498db",
                                      hover_color="#2980b9",
                                      height=45,
                                      width=200,
                                      font=ctk.CTkFont(size=13, weight="bold"))
        else:
            btn_guardar = ctk.CTkButton(botones_frame,
                                      text="➕ AGREGAR USUARIO",
                                      command=lambda: self.guardar_nuevo_usuario(
                                          self.entries['usuario'].get(),
                                          self.entry_password.get(),
                                          self.entry_confirmar.get(),
                                          self.entries['rol'].get()
                                      ),
                                      fg_color="#2ecc71",
                                      hover_color="#27ae60",
                                      height=45,
                                      width=200,
                                      font=ctk.CTkFont(size=13, weight="bold"))
        
        btn_guardar.pack(side='left', padx=15)
        
        btn_cancelar = ctk.CTkButton(botones_frame,
                                   text="❌ CANCELAR",
                                   command=ventana.destroy,
                                   fg_color="#95a5a6",
                                   hover_color="#7f8c8d",
                                   height=45,
                                   width=150,
                                   font=ctk.CTkFont(size=13, weight="bold"))
        btn_cancelar.pack(side='left', padx=15)
        
        # Asegurar que la ventana se muestre correctamente
        ventana.update()
        
        # Poner foco en el campo usuario
        entry_usuario.focus()
    
    def toggle_campos_password(self, frame, row_offset):
        """Muestra u oculta los campos de contraseña (CORREGIDA)"""
        if hasattr(self, 'frame_password'):
            if self.cambiar_password_var.get():
                self.frame_password.grid()
                self.entry_password.configure(state='normal')
                self.entry_confirmar.configure(state='normal')
                self.entry_password.focus()
            else:
                self.frame_password.grid_remove()
                if hasattr(self, 'entry_password'):
                    self.entry_password.delete(0, tk.END)
                if hasattr(self, 'entry_confirmar'):
                    self.entry_confirmar.delete(0, tk.END)
                self.entry_password.configure(state='disabled')
                self.entry_confirmar.configure(state='disabled')
    
    def guardar_nuevo_usuario(self, usuario, password, confirmar_password, rol):
        """Guarda un nuevo usuario"""
        if not usuario or not password:
            messagebox.showwarning("Advertencia", "⚠️ Usuario y contraseña son obligatorios")
            return
        
        if password != confirmar_password:
            messagebox.showwarning("Advertencia", "⚠️ Las contraseñas no coinciden")
            return
        
        if len(password) < 4:
            messagebox.showwarning("Advertencia", "⚠️ La contraseña debe tener al menos 4 caracteres")
            return
        
        resultado = agregar_usuario(usuario, password, rol)
        
        if resultado == True:
            messagebox.showinfo("Éxito", "✅ Usuario agregado correctamente")
            self.ventana_agregar.destroy()
            self.actualizar_lista()
        elif resultado == "usuario_existe":
            messagebox.showerror("Error", "❌ El nombre de usuario ya existe")
        else:
            messagebox.showerror("Error", "❌ No se pudo agregar el usuario")
    
    def guardar_edicion_usuario(self, id_usuario, usuario, rol, cambiar_password, password, confirmar_password):
        """Guarda los cambios de un usuario editado"""
        if not usuario:
            messagebox.showwarning("Advertencia", "⚠️ El usuario es obligatorio")
            return
        
        if cambiar_password:
            if not password:
                messagebox.showwarning("Advertencia", "⚠️ Ingrese la nueva contraseña")
                return
            
            if password != confirmar_password:
                messagebox.showwarning("Advertencia", "⚠️ Las contraseñas no coinciden")
                return
            
            if len(password) < 4:
                messagebox.showwarning("Advertencia", "⚠️ La contraseña debe tener al menos 4 caracteres")
                return
        
        if actualizar_usuario(id_usuario, usuario, rol, cambiar_password, password if cambiar_password else None):
            messagebox.showinfo("Éxito", "✅ Usuario actualizado correctamente")
            self.ventana_editar.destroy()
            self.actualizar_lista()
        else:
            messagebox.showerror("Error", "❌ No se pudo actualizar el usuario")
    
    def mostrar_eliminar_usuario(self):
        """Elimina el usuario seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "⚠️ Por favor seleccione un usuario para eliminar")
            return
        
        item = self.tree.item(seleccion[0])
        id_usuario = item['values'][0]
        nombre_usuario = item['values'][1]
        rol_usuario = item['values'][2]
        
        # No permitir eliminarse a sí mismo
        if self.usuario_actual and self.usuario_actual == nombre_usuario:
            messagebox.showwarning("Advertencia", "❌ No puede eliminar su propio usuario")
            return
        
        respuesta = messagebox.askyesno("Confirmar Eliminación", 
                                       f"¿Está seguro de eliminar el usuario?\n\n"
                                       f"👤 Usuario: {nombre_usuario}\n"
                                       f"👑 Rol: {rol_usuario}\n\n"
                                       f"⚠️ Esta acción no se puede deshacer.")
        if respuesta:
            resultado = eliminar_usuario(id_usuario)
            
            if resultado == True:
                messagebox.showinfo("Éxito", "✅ Usuario eliminado correctamente")
                self.actualizar_lista()
            elif resultado == "ultimo_admin":
                messagebox.showerror("Error", "❌ No se puede eliminar el último administrador del sistema")
            else:
                messagebox.showerror("Error", "❌ No se pudo eliminar el usuario")
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas de usuarios"""
        usuarios = obtener_usuarios()
        if not usuarios:
            messagebox.showinfo("Estadísticas", "📊 No hay usuarios registrados")
            return
        
        total_usuarios = len(usuarios)
        jefes = sum(1 for u in usuarios if u['Rol'].lower() == 'jefe')
        trabajadores = sum(1 for u in usuarios if u['Rol'].lower() == 'trabajador')
        vendedores = sum(1 for u in usuarios if u['Rol'].lower() == 'vendedor')
        
        estadisticas = (
            f"📊 ESTADÍSTICAS DE USUARIOS\n\n"
            f"👥 Total de usuarios: {total_usuarios}\n"
            f"👑 Jefes: {jefes}\n"
            f"👨‍💼 Trabajadores: {trabajadores}\n"
            f"💰 Vendedores: {vendedores}\n\n"
            f"📈 Distribución:\n"
            f"• Jefes: {jefes/total_usuarios*100:.1f}%\n"
            f"• Trabajadores: {trabajadores/total_usuarios*100:.1f}%\n"
            f"• Vendedores: {vendedores/total_usuarios*100:.1f}%"
        )
        
        messagebox.showinfo("Estadísticas de Usuarios", estadisticas)
    
    # ============================================
    # MÉTODOS DE NAVEGACIÓN Y UTILIDAD
    # ============================================
    
    def volver_punto_venta(self):
        """Regresa al punto de venta principal"""
        self.root.destroy()
        if self.user_app_ref:
            self.user_app_ref.root.deiconify()
    
    def centrar_ventana(self, ventana, ancho, alto):
        """Centra una ventana en la pantalla"""
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

if __name__ == "__main__":
    root = ctk.CTk()
    app = UsuariosView(root, usuario_actual="admin")
    root.mainloop()