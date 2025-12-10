# servicios_viw.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from servicios_controller import ver_servicios, agregar_servicio, editar_servicio, eliminar_servicio, obtener_servicio_por_id

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")
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

class ModernToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tip_window:
            return
        
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tip_window, text=self.text, 
                        justify='left', relief='solid', borderwidth=1,
                        bg="#ffffe0", fg="black", font=("Arial", 9))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class ServiciosView:
    def __init__(self, root, parent=None):
        """
        Args:
            root: Ventana principal
            parent: Referencia a UserApp2 para poder volver
        """
        self.root = root
        self.parent = parent  # Referencia a UserApp2
        self.root.title("Gestión de Servicios - Barbería Bravo")
        
        # TAMAÑO MÁS GRANDE - 1400x850
        self.root.geometry("1400x850")
        
        # Centrar ventana
        self.root.update_idletasks()
        ancho = 1400
        alto = 850
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # Hacer que la ventana sea redimensionable
        self.root.resizable(True, True)
        
        self.menu_abierto = False
        self.logo = cargar_imagen("c9141f85-d013-448a-aea0-2201255befd4.jpg", tamaño=(70, 70))  # Logo más grande
        self.servicio_editando = None
        
        # Configurar el cierre para volver a UserApp2
        if self.parent:
            self.root.protocol("WM_DELETE_WINDOW", self.cerrar_y_volver)
        
        self.crear_elementos()
        self.actualizar_tabla()
        self.root.focus_set()

    def crear_elementos(self):
        # ============================================
        # 1. HEADER SUPERIOR (MÁS GRANDE)
        # ============================================
        header_frame = ctk.CTkFrame(self.root, height=100, corner_radius=0, fg_color="#1a1a1a")  # Más alto
        header_frame.pack(fill='x', side='top')
        
        # Logo y título
        if self.logo:
            img_label = ctk.CTkLabel(header_frame, image=self.logo, text="", fg_color="#1a1a1a")
            img_label.pack(side='left', padx=(30, 20), pady=15)  # Más padding
        
        ctk.CTkLabel(header_frame, 
                     text="🛠️ GESTIÓN DE SERVICIOS - BARBERÍA BRAVO", 
                     font=ctk.CTkFont(family="Arial", size=26, weight="bold"),  # Fuente más grande
                     text_color="white").pack(side='left', padx=10, pady=15)
        
        # Botones de control
        control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        control_frame.pack(side='right', padx=30, pady=15)
        
        btn_volver = ctk.CTkButton(control_frame,
                                 text="↶ VOLVER AL PUNTO DE VENTA",
                                 command=self.cerrar_y_volver,
                                 fg_color="#3498db",
                                 hover_color="#2980b9",
                                 width=220,  # Más ancho
                                 height=40,  # Más alto
                                 font=ctk.CTkFont(size=13, weight="bold"))  # Fuente más grande
        btn_volver.pack(side='left', padx=8)
        
        btn_exportar = ctk.CTkButton(control_frame,
                                   text="📊 VER ESTADÍSTICAS",
                                   command=self.mostrar_estadisticas,
                                   fg_color="#2ecc71",
                                   hover_color="#27ae60",
                                   width=180,
                                   height=40,
                                   font=ctk.CTkFont(size=13, weight="bold"))
        btn_exportar.pack(side='left', padx=8)
        
        # Botón hamburguesa (más grande)
        self.btn_hamburguesa = ctk.CTkButton(header_frame, 
                                            text="☰ MENÚ", 
                                            width=80,  # Más ancho
                                            height=40,  # Más alto
                                            command=self.toggle_menu,
                                            fg_color="#555555",
                                            hover_color="#777777",
                                            font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_hamburguesa.pack(side='right', padx=(0, 20), pady=15)
        
        # ============================================
        # 2. PANEL DE MENÚ LATERAL (MÁS ANCHO)
        # ============================================
        self.panel_menu = ctk.CTkFrame(self.root, width=250, corner_radius=0, fg_color="#2c3e50")  # Más ancho
        self.panel_menu.place(x=-250, y=100, relheight=1)
        
        opciones = [
            ("🔄 ACTUALIZAR LISTA", self.actualizar_tabla),
            ("📊 VER ESTADÍSTICAS", self.mostrar_estadisticas),
            ("📋 AGREGAR NUEVO SERVICIO", self.limpiar_formulario),
            ("↶ VOLVER AL PUNTO DE VENTA", self.cerrar_y_volver),
            ("❌ CERRAR VENTANA", self.root.destroy)
        ]

        for i, (texto, comando) in enumerate(opciones):
            btn = ctk.CTkButton(self.panel_menu, text=texto,
                              command=comando,
                              fg_color="transparent",
                              hover_color="#34495e",
                              text_color="white",
                              font=ctk.CTkFont(family="Arial", size=13),  # Fuente más grande
                              anchor='w',
                              height=50,  # Más alto
                              width=230)  # Más ancho
            btn.place(x=10, y=30 + i*55)  # Más espacio entre botones
        
        # ============================================
        # 3. CONTENIDO PRINCIPAL
        # ============================================
        main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)  # Más padding
        
        # Dividir en dos columnas: formulario izquierdo (40%), tabla derecha (60%)
        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # ============================================
        # 4. PANEL IZQUIERDO (FORMULARIO - MÁS GRANDE)
        # ============================================
        left_panel = ctk.CTkFrame(main_frame, corner_radius=12)  # Bordes más redondeados
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 15), pady=10)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Título del formulario (más grande)
        form_header = ctk.CTkFrame(left_panel, fg_color="#34495e", corner_radius=10)
        form_header.grid(row=0, column=0, sticky='ew', padx=12, pady=(12, 8))
        
        self.form_title = ctk.CTkLabel(form_header, 
                                      text="➕ AGREGAR NUEVO SERVICIO",
                                      font=ctk.CTkFont(family="Arial", size=18, weight="bold"),  # Más grande
                                      text_color="white")
        self.form_title.pack(pady=15)
        
        # Formulario
        form_frame = ctk.CTkFrame(left_panel, corner_radius=10)
        form_frame.grid(row=1, column=0, sticky='nsew', padx=12, pady=(8, 12))
        
        # Campos del formulario (más grandes)
        campos = [
            ("Nombre del Servicio:", "entry_nombre", True),
            ("Descripción:", "entry_descripcion", False),
            ("Duración (minutos):", "entry_duracion", False),
            ("Precio ($):", "entry_precio", True)
        ]
        
        for i, (label_text, attr_name, required) in enumerate(campos):
            # Etiqueta (más grande)
            label = ctk.CTkLabel(form_frame,
                                text=f"{label_text}{' *' if required else ''}",
                                font=ctk.CTkFont(size=14, weight="bold"),  # Más grande
                                text_color="#2c3e50")
            label.grid(row=i*2, column=0, padx=25, pady=(20 if i == 0 else 12), sticky='w')  # Más padding
            
            # Campo de entrada (más grande)
            entry_width = 300  # Más ancho
            entry_height = 40  # Más alto
            
            entry = ctk.CTkEntry(form_frame,
                                width=entry_width,
                                height=entry_height,
                                font=ctk.CTkFont(size=13),  # Fuente más grande
                                placeholder_text=f"Ingrese {label_text.lower()[:-1]}" if not required else "")
            
            if attr_name == "entry_duracion":
                entry.configure(placeholder_text="Ej: 30 (opcional)")
            elif attr_name == "entry_precio":
                entry.configure(placeholder_text="Ej: 25.50")
            
            entry.grid(row=i*2 + 1, column=0, padx=25, pady=(0, 20 if i == len(campos)-1 else 8), sticky='w')
            
            # Guardar referencia al campo
            setattr(self, attr_name, entry)
        
        # Botones del formulario (más grandes)
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=8, column=0, pady=25)
        
        self.btn_agregar = ctk.CTkButton(btn_frame,
                                       text="➕ AGREGAR SERVICIO",
                                       command=self.agregar_servicio,
                                       fg_color="#2ecc71",
                                       hover_color="#27ae60",
                                       height=45,  # Más alto
                                       width=280,  # Más ancho
                                       font=ctk.CTkFont(size=13, weight="bold"),  # Fuente más grande
                                       corner_radius=10)  # Más redondeado
        self.btn_agregar.pack(pady=8)
        
        self.btn_editar = ctk.CTkButton(btn_frame,
                                      text="✏️ EDITAR SERVICIO",
                                      command=self.editar_servicio,
                                      fg_color="#f39c12",
                                      hover_color="#d68910",
                                      height=45,
                                      width=280,
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      corner_radius=10,
                                      state='disabled')
        self.btn_editar.pack(pady=8)
        
        self.btn_cancelar = ctk.CTkButton(btn_frame,
                                        text="❌ CANCELAR EDICIÓN",
                                        command=self.cancelar_edicion,
                                        fg_color="#e74c3c",
                                        hover_color="#c0392b",
                                        height=40,
                                        width=280,
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        corner_radius=8,
                                        state='disabled')
        self.btn_cancelar.pack(pady=8)
        
        # ============================================
        # 5. PANEL DERECHO (TABLA DE SERVICIOS - MÁS GRANDE)
        # ============================================
        right_panel = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#ecf0f1")
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(15, 0), pady=10)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # Título de la tabla (más grande)
        table_header = ctk.CTkFrame(right_panel, fg_color="#2c3e50", corner_radius=10)
        table_header.grid(row=0, column=0, sticky='ew', padx=12, pady=(12, 8))
        
        ctk.CTkLabel(table_header,
                     text="📋 LISTA DE SERVICIOS REGISTRADOS",
                     font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                     text_color="white").pack(pady=15)
        
        # Frame para treeview
        tree_frame = ctk.CTkFrame(right_panel, corner_radius=10)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=12, pady=(8, 12))
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
        self.tree = ttk.Treeview(tree_frame,
                                columns=("id", "nombre", "descripcion", "duracion", "precio"),
                                show="headings",
                                height=18)  # Más filas visibles
        
        # Configurar columnas (más anchas)
        column_configs = [
            ("id", "ID", 80),        # Más ancho
            ("nombre", "NOMBRE", 200),  # Más ancho
            ("descripcion", "DESCRIPCIÓN", 300),  # Más ancho
            ("duracion", "DURACIÓN", 120),  # Más ancho
            ("precio", "PRECIO ($)", 120)  # Más ancho
        ]
        
        for col_name, heading, width in column_configs:
            self.tree.heading(col_name, text=heading)
            self.tree.column(col_name, width=width, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars (más grandes)
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Scrollbar horizontal
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky='ew', columnspan=2)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Botones de acción en la tabla (más grandes)
        action_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky='ew', padx=12, pady=(0, 15))
        
        btn_actualizar = ctk.CTkButton(action_frame,
                                      text="🔄 ACTUALIZAR LISTA",
                                      command=self.actualizar_tabla,
                                      fg_color="#3498db",
                                      hover_color="#2980b9",
                                      height=45,  # Más alto
                                      width=160,  # Más ancho
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      corner_radius=8)
        btn_actualizar.pack(side='left', padx=8)
        
        btn_eliminar = ctk.CTkButton(action_frame,
                                   text="🗑️ ELIMINAR SELECCIONADO",
                                   command=self.eliminar_servicio,
                                   fg_color="#e74c3c",
                                   hover_color="#c0392b",
                                   height=45,
                                   width=180,
                                   font=ctk.CTkFont(size=13, weight="bold"),
                                   corner_radius=8)
        btn_eliminar.pack(side='right', padx=8)
        
        # Botón para limpiar selección
        btn_limpiar = ctk.CTkButton(action_frame,
                                  text="🗙 LIMPIAR SELECCIÓN",
                                  command=self.cancelar_edicion,
                                  fg_color="#95a5a6",
                                  hover_color="#7f8c8d",
                                  height=45,
                                  width=160,
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  corner_radius=8)
        btn_limpiar.pack(side='left', padx=8)
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_servicio)
        self.tree.bind('<Double-1>', lambda e: self.seleccionar_servicio(e))
        
        # Añadir tooltips a los botones
        ModernToolTip(self.btn_agregar, "Agregar un nuevo servicio a la base de datos")
        ModernToolTip(self.btn_editar, "Guardar cambios en el servicio seleccionado")
        ModernToolTip(self.btn_cancelar, "Cancelar la edición y limpiar el formulario")
        ModernToolTip(btn_actualizar, "Actualizar la lista de servicios desde la base de datos")
        ModernToolTip(btn_eliminar, "Eliminar el servicio seleccionado")
        ModernToolTip(btn_limpiar, "Deseleccionar servicio y limpiar el formulario")
        ModernToolTip(btn_volver, "Volver a la pantalla principal de punto de venta")
        ModernToolTip(btn_exportar, "Ver estadísticas de los servicios")
    
    # ============================================
    # MÉTODOS DEL MENÚ HAMBURGUESA
    # ============================================
    def toggle_menu(self):
        """Alterna el estado del menú lateral"""
        if not self.menu_abierto:
            self.panel_menu.place(x=0, y=100)
            self.panel_menu.lift()
            self.menu_abierto = True
        else:
            self.panel_menu.place(x=-250, y=100)
            self.menu_abierto = False
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas de servicios"""
        servicios = ver_servicios()
        if not servicios:
            messagebox.showinfo("Estadísticas", "No hay servicios registrados.")
            return
        
        total_servicios = len(servicios)
        precios = [float(s[4]) for s in servicios]
        duraciones = [int(s[3] or 0) for s in servicios]
        
        precio_promedio = sum(precios) / total_servicios if total_servicios > 0 else 0
        duracion_promedio = sum(duraciones) / total_servicios if total_servicios > 0 else 0
        
        # Crear ventana de estadísticas más grande
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title("📊 Estadísticas de Servicios")
        stats_window.geometry("600x500")
        
        # Centrar ventana
        stats_window.update_idletasks()
        ancho = stats_window.winfo_width()
        alto = stats_window.winfo_height()
        x = (stats_window.winfo_screenwidth() // 2) - (ancho // 2)
        y = (stats_window.winfo_screenheight() // 2) - (alto // 2)
        stats_window.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(stats_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(main_frame,
                     text="📊 ESTADÍSTICAS DE SERVICIOS",
                     font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
                     text_color="#2c3e50").pack(pady=20)
        
        # Frame para estadísticas
        stats_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#ecf0f1")
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear etiquetas de estadísticas
        stats_data = [
            (f"📈 Total de servicios:", f"{total_servicios}", "#3498db"),
            (f"💰 Precio promedio:", f"${precio_promedio:.2f}", "#2ecc71"),
            (f"⏱️ Duración promedio:", f"{duracion_promedio:.0f} minutos", "#f39c12"),
            (f"🎯 Servicio más caro:", f"${max(precios):.2f}", "#e74c3c"),
            (f"🎯 Servicio más económico:", f"${min(precios):.2f}", "#9b59b6")
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            frame.pack(fill='x', padx=20, pady=15)
            
            ctk.CTkLabel(frame,
                        text=label,
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color="#2c3e50").pack(side='left')
            
            ctk.CTkLabel(frame,
                        text=value,
                        font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=color).pack(side='right')
        
        # Botón cerrar
        btn_cerrar = ctk.CTkButton(main_frame,
                                  text="CERRAR",
                                  command=stats_window.destroy,
                                  fg_color="#95a5a6",
                                  hover_color="#7f8c8d",
                                  height=40,
                                  width=150,
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  corner_radius=8)
        btn_cerrar.pack(pady=20)
        
        self.toggle_menu()
    
    # ============================================
    # MÉTODOS DE GESTIÓN DE SERVICIOS
    # ============================================
    def agregar_servicio(self):
        """Agrega un nuevo servicio"""
        nombre = self.entry_nombre.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        duracion = self.entry_duracion.get().strip()
        precio = self.entry_precio.get().strip()
        
        # Validaciones
        if not nombre:
            messagebox.showwarning("Error", "El nombre del servicio es obligatorio.")
            self.entry_nombre.focus_set()
            return
        
        if not precio:
            messagebox.showwarning("Error", "El precio del servicio es obligatorio.")
            self.entry_precio.focus_set()
            return
        
        # Validar precio
        try:
            precio_float = float(precio)
            if precio_float <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "El precio debe ser un número mayor a 0.")
            self.entry_precio.focus_set()
            return
        
        # Validar duración si se proporciona
        duracion_int = None
        if duracion:
            try:
                duracion_int = int(duracion)
                if duracion_int <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Error", "La duración debe ser un número entero mayor a 0.")
                self.entry_duracion.focus_set()
                return
        
        # Verificar si ya existe un servicio con el mismo nombre
        servicios = ver_servicios()
        for servicio in servicios:
            if servicio[1].lower() == nombre.lower():
                respuesta = messagebox.askyesno(
                    "Servicio Existente",
                    f"Ya existe un servicio llamado '{servicio[1]}'.\n¿Desea editarlo en lugar de crear uno nuevo?"
                )
                if respuesta:
                    self.servicio_editando = servicio[0]
                    self.cargar_formulario_edicion(servicio)
                    return
                else:
                    return
        
        # Agregar servicio
        if agregar_servicio(nombre, descripcion, duracion_int, precio_float):
            messagebox.showinfo("Éxito", f"✅ Servicio '{nombre}' agregado correctamente.")
            self.limpiar_formulario()
            self.actualizar_tabla()
            self.form_title.configure(text="➕ AGREGAR NUEVO SERVICIO")
        else:
            messagebox.showerror("Error", "❌ No se pudo agregar el servicio.")
    
    def editar_servicio(self):
        """Edita un servicio existente"""
        if not self.servicio_editando:
            messagebox.showwarning("Advertencia", "No hay servicio seleccionado para editar.")
            return
        
        nombre = self.entry_nombre.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        duracion = self.entry_duracion.get().strip()
        precio = self.entry_precio.get().strip()
        
        # Validaciones
        if not nombre:
            messagebox.showwarning("Error", "El nombre del servicio es obligatorio.")
            self.entry_nombre.focus_set()
            return
        
        if not precio:
            messagebox.showwarning("Error", "El precio del servicio es obligatorio.")
            self.entry_precio.focus_set()
            return
        
        # Validar precio
        try:
            precio_float = float(precio)
            if precio_float <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "El precio debe ser un número mayor a 0.")
            self.entry_precio.focus_set()
            return
        
        # Validar duración si se proporciona
        duracion_int = None
        if duracion:
            try:
                duracion_int = int(duracion)
                if duracion_int <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Error", "La duración debe ser un número entero mayor a 0.")
                self.entry_duracion.focus_set()
                return
        
        # Editar servicio
        if editar_servicio(self.servicio_editando, nombre, descripcion, duracion_int, precio_float):
            messagebox.showinfo("Éxito", f"✅ Servicio '{nombre}' actualizado correctamente.")
            self.cancelar_edicion()
            self.actualizar_tabla()
        else:
            messagebox.showerror("Error", "❌ No se pudo actualizar el servicio.")
    
    def eliminar_servicio(self):
        """Elimina el servicio seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un servicio para eliminar.")
            return
        
        item = self.tree.item(seleccion[0])
        servicio_id = item['values'][0]
        servicio_nombre = item['values'][1]
        servicio_precio = item['values'][4]
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Está seguro de eliminar el servicio?\n\n"
            f"📝 Nombre: {servicio_nombre}\n"
            f"💰 Precio: {servicio_precio}\n\n"
            f"⚠️ Esta acción no se puede deshacer."
        )
        
        if respuesta:
            if eliminar_servicio(servicio_id):
                messagebox.showinfo("Éxito", "✅ Servicio eliminado correctamente.")
                self.actualizar_tabla()
                self.cancelar_edicion()
            else:
                messagebox.showerror("Error", "❌ No se pudo eliminar el servicio.")
    
    def seleccionar_servicio(self, event):
        """Selecciona un servicio para editar"""
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])
            servicio_id = item['values'][0]
            
            # Obtener datos completos del servicio
            servicio_completo = obtener_servicio_por_id(servicio_id)
            if servicio_completo:
                self.servicio_editando = servicio_id
                self.cargar_formulario_edicion(servicio_completo)
    
    def cargar_formulario_edicion(self, servicio):
        """Carga los datos de un servicio en el formulario para editar"""
        # Llenar formulario con datos del servicio
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, servicio[1])
        
        self.entry_descripcion.delete(0, tk.END)
        self.entry_descripcion.insert(0, servicio[2] if servicio[2] else "")
        
        self.entry_duracion.delete(0, tk.END)
        self.entry_duracion.insert(0, servicio[3] if servicio[3] else "")
        
        self.entry_precio.delete(0, tk.END)
        self.entry_precio.insert(0, servicio[4])
        
        # Cambiar estado de botones y título
        self.form_title.configure(text="✏️ EDITAR SERVICIO")
        self.btn_agregar.configure(state='disabled')
        self.btn_editar.configure(state='normal')
        self.btn_cancelar.configure(state='normal')
        
        # Resaltar fila seleccionada
        for item in self.tree.selection():
            self.tree.selection_set(item)
    
    def cancelar_edicion(self):
        """Cancela la edición y limpia el formulario"""
        self.servicio_editando = None
        self.limpiar_formulario()
        self.form_title.configure(text="➕ AGREGAR NUEVO SERVICIO")
        self.btn_agregar.configure(state='normal')
        self.btn_editar.configure(state='disabled')
        self.btn_cancelar.configure(state='disabled')
        self.tree.selection_remove(self.tree.selection())
    
    def limpiar_formulario(self):
        """Limpia el formulario"""
        self.entry_nombre.delete(0, tk.END)
        self.entry_descripcion.delete(0, tk.END)
        self.entry_duracion.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.entry_nombre.focus_set()
    
    def actualizar_tabla(self):
        """Actualiza la tabla de servicios"""
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Cargar servicios
        try:
            servicios = ver_servicios()
            if servicios:
                for servicio in servicios:
                    # Formatear precio
                    precio_formateado = f"${float(servicio[4]):.2f}"
                    
                    self.tree.insert("", tk.END, values=(
                        servicio[0],          # ID
                        servicio[1],          # Nombre
                        servicio[2] or "",    # Descripción
                        servicio[3] or "",    # Duración
                        precio_formateado      # Precio
                    ))
                
                # Mostrar estadísticas rápidas
                total_servicios = len(servicios)
                self.form_title.configure(text=f"➕ AGREGAR NUEVO SERVICIO | Total: {total_servicios}")
            else:
                self.form_title.configure(text="➕ AGREGAR NUEVO SERVICIO")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los servicios: {str(e)}")
    
    def cerrar_y_volver(self):
        """Cierra ServiciosView y vuelve a UserApp2"""
        if self.parent:
            self.root.destroy()
            self.parent.root.deiconify()  # Muestra nuevamente UserApp2
        else:
            self.root.destroy()
    
    def __del__(self):
        """Destructor - asegura que UserApp2 se muestre al cerrar"""
        if self.parent:
            self.parent.root.deiconify()

if __name__ == "__main__":
    # Para pruebas independientes
    root = ctk.CTk()
    app = ServiciosView(root)
    root.mainloop()