import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from datetime import datetime
import uuid

# Importaciones de tus controladores (mantén estas)
from poductos_controller import ver_producto
from servicios_viw import ServiciosView
from servicios_controller import ver_servicios
from historial_controller import guardar_venta, obtener_id_usuario
from login_controller import obtener_tipo_usuario
from Stock_viw import Stockview
from Stock_controller import disminuir_stock, verificar_stock
from usuarios_viw import UsuariosView

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")  # "dark", "light", "system"
ctk.set_default_color_theme("blue")

def cargar_imagen(ruta, tamaño=(80, 80)):
    try:
        img = Image.open(ruta)
        img = img.resize(tamaño, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=tamaño)
    except Exception as e:
        print(f"Error al cargar imagen {ruta}: {e}")
        # Imagen por defecto si no se encuentra
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

class UserApp2:
    def __init__(self, username, tipo_usuario=None):
        self.username = username
        self.id_usuario = obtener_id_usuario(username)
        
        if tipo_usuario is None:
            self.tipo_usuario = obtener_tipo_usuario(username)
        else:
            self.tipo_usuario = tipo_usuario
            
        self.carrito = []
        self.root = ctk.CTk()
        
        # Configuración de ventana normal (NO pantalla completa)
        self.root.geometry("1300x750")  # Tamaño normal de ventana
        self.root.title(f"Punto de Venta - {username}")
        
        # Centrar la ventana en la pantalla
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        self.logo = cargar_imagen("c9141f85-d013-448a-aea0-2201255befd4.jpg", tamaño=(60, 60))
        self.menu_abierto = False
        
        self.servicios_disponibles = self.cargar_servicios()
        
        self.crear_elementos()
        self.ver_productos()
        self.root.mainloop()
    
    def volver_al_punto_venta(self):
        """Método para que StockView pueda regresar aquí"""
        self.root.deiconify()

    def cargar_servicios(self):
        try:
            servicios = ver_servicios()
            servicios_formateados = []
            for servicio in servicios:
                servicios_formateados.append({
                    'id': servicio[0],
                    'nombre': servicio[1],
                    'descripcion': servicio[2],
                    'duracion': servicio[3],
                    'precio': float(servicio[4])
                })
            return servicios_formateados
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los servicios: {str(e)}")
            return []

    def crear_elementos(self):
        # ============================================
        # 1. HEADER SUPERIOR
        # ============================================
        header_frame = ctk.CTkFrame(self.root, height=80, corner_radius=0, fg_color="#1a1a1a")
        header_frame.pack(fill='x', side='top')
        
        # Logo y título
        if self.logo:
            img_label = ctk.CTkLabel(header_frame, image=self.logo, text="", fg_color="#1a1a1a")
            img_label.pack(side='left', padx=(20, 10), pady=10)
        
        ctk.CTkLabel(header_frame, 
                     text="SISTEMA DE PUNTO DE VENTA", 
                     font=ctk.CTkFont(family="Arial", size=22, weight="bold"), 
                     text_color="white").pack(side='left', padx=10, pady=10)
        
        # Información del usuario
        user_info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        user_info_frame.pack(side='right', padx=20, pady=10)
        
        tipo_texto = "Jefe" if self.tipo_usuario == 'jefe' else "Trabajador"
        ctk.CTkLabel(user_info_frame, 
                     text=f"👤 {self.username} ({tipo_texto})", 
                     font=ctk.CTkFont(size=12),
                     text_color="#cccccc").pack(side='top', anchor='e')
        
        # Botón hamburguesa
        self.btn_hamburguesa = ctk.CTkButton(header_frame, 
                                            text="☰ Menú", 
                                            width=100,
                                            height=35,
                                            command=self.toggle_menu,
                                            fg_color="#3498db",
                                            hover_color="#2980b9",
                                            font=ctk.CTkFont(weight="bold"))
        self.btn_hamburguesa.pack(side='right', padx=(0, 10), pady=10)
        
        # ============================================
        # 2. PANEL DE MENÚ LATERAL
        # ============================================
        self.panel_menu = ctk.CTkFrame(self.root, width=250, corner_radius=0, fg_color="#2c3e50")
        self.panel_menu.place(x=-250, y=80, relheight=1)
        
        opciones_menu = []
        
        # Opciones para ambos tipos de usuarios
        opciones_menu.append(("📊 Historial de ventas", self.history_product, True))
        opciones_menu.append(("🔄 Cerrar Sesión", self.cerrar_sesion, True))
        
        # Opciones específicas según tipo de usuario
        if self.tipo_usuario == 'jefe':
            opciones_menu.append(("📦 Gestión de Productos", self.gestionar_productos, True))
            opciones_menu.append(("🛠️ Gestión Servicios", self.gestionar_servicios, True))
            opciones_menu.append(("👥 Gestión de Usuarios", self.abrir_user_view, True))
        
        opciones_menu.append(("✖️ Salir Sistema", self.salir_sistema, True))
        
        # Crear botones del menú
        for i, (texto, comando, visible) in enumerate(opciones_menu):
            if visible:
                btn = ctk.CTkButton(self.panel_menu, text=texto,
                                  command=comando,
                                  fg_color="transparent",
                                  hover_color="#34495e",
                                  text_color="white",
                                  font=ctk.CTkFont(family="Arial", size=13),
                                  anchor='w',
                                  height=45,
                                  width=230)
                btn.place(x=10, y=30 + i*50)
        
        # ============================================
        # 3. CONTENIDO PRINCIPAL
        # ============================================
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Dividir en dos columnas principales
        main_container.grid_columnconfigure(0, weight=3)  # Productos y servicios (70%)
        main_container.grid_columnconfigure(1, weight=1)  # Carrito (30%)
        main_container.grid_rowconfigure(0, weight=1)
        
        # ============================================
        # 4. PANEL IZQUIERDO (PRODUCTOS Y SERVICIOS)
        # ============================================
        left_panel = ctk.CTkFrame(main_container, corner_radius=10)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Sección de Servicios Rápidos
        servicios_frame = ctk.CTkFrame(left_panel, corner_radius=8, fg_color="#34495e")
        servicios_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(servicios_frame, 
                     text="⚡ SERVICIOS RÁPIDOS", 
                     font=ctk.CTkFont(family="Arial", size=16, weight="bold"), 
                     text_color="white").pack(side='top', pady=(12, 10))
        
        servicios_container = ctk.CTkFrame(servicios_frame, fg_color="transparent")
        servicios_container.pack(fill='x', pady=(0, 10), padx=10)
        
        if not self.servicios_disponibles:
            ctk.CTkLabel(servicios_container, 
                         text="No hay servicios disponibles", 
                         text_color="#ecf0f1", 
                         font=ctk.CTkFont(size=12)).pack(pady=20)
        else:
            # Crear grid para los botones de servicios (2x2)
            for row in range(2):
                servicios_container.grid_rowconfigure(row, weight=1)
            for col in range(2):
                servicios_container.grid_columnconfigure(col, weight=1)
            
            for i, servicio in enumerate(self.servicios_disponibles[:4]):  # Mostrar máximo 4 servicios
                btn_text = f"{servicio['nombre']}\n${servicio['precio']:.2f}"
                
                btn_servicio = ctk.CTkButton(
                    servicios_container,
                    text=btn_text,
                    height=70,
                    command=lambda s=servicio: self.agregar_servicio(s),
                    fg_color="#3498db",
                    hover_color="#2980b9",
                    text_color="white",
                    font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
                    corner_radius=6
                )
                
                # Crear tooltip para la descripción
                tooltip_text = f"{servicio['descripcion']}\nDuración: {servicio['duracion']} min"
                ModernToolTip(btn_servicio, tooltip_text)
                
                btn_servicio.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='nsew')
        
        # Sección de Productos
        productos_frame = ctk.CTkFrame(left_panel, corner_radius=8)
        productos_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(5, 10))
        productos_frame.grid_columnconfigure(0, weight=1)
        productos_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(productos_frame, 
                     text="🛒 AGREGAR PRODUCTOS", 
                     font=ctk.CTkFont(family="Arial", size=16, weight="bold"), 
                     text_color="#2c3e50").grid(row=0, column=0, padx=20, pady=(15, 10), sticky='w')
        
        # Formulario para agregar productos
        form_frame = ctk.CTkFrame(productos_frame, fg_color="transparent")
        form_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 15))
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Producto
        ctk.CTkLabel(form_frame, 
                     text="Producto:", 
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0, 10), pady=10, sticky='w')
        
        self.combo_productos = ctk.CTkComboBox(form_frame,
                                             command=self.actualizar_precio,
                                             values=[],
                                             state="readonly",
                                             font=ctk.CTkFont(size=12),
                                             height=35,
                                             dropdown_font=ctk.CTkFont(size=11))
        self.combo_productos.grid(row=0, column=1, columnspan=2, padx=5, pady=10, sticky='ew')
        
        # Cantidad
        ctk.CTkLabel(form_frame, 
                     text="Cantidad:", 
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=(0, 10), pady=10, sticky='w')
        
        self.entry_cantidad = ctk.CTkEntry(form_frame, 
                                          width=100, 
                                          font=ctk.CTkFont(size=12), 
                                          height=35)
        self.entry_cantidad.grid(row=1, column=1, padx=5, pady=10, sticky='w')
        self.entry_cantidad.insert(0, "1")
        
        # Precio
        ctk.CTkLabel(form_frame, 
                     text="Precio:", 
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=2, padx=(20, 10), pady=10, sticky='w')
        
        self.label_precio = ctk.CTkLabel(form_frame, 
                                        text="$0.00",
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        text_color="#27ae60")
        self.label_precio.grid(row=1, column=3, padx=5, pady=10, sticky='w')
        
        # Información de stock
        self.label_stock_info = ctk.CTkLabel(form_frame, 
                                           text="",
                                           font=ctk.CTkFont(size=11),
                                           text_color="#7f8c8d")
        self.label_stock_info.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='w')
        
        # Botón Agregar
        btn_agregar = ctk.CTkButton(form_frame, 
                                   text="➕ AGREGAR AL CARRITO",
                                   command=self.agregar_al_carrito,
                                   fg_color="#2ecc71",
                                   hover_color="#27ae60",
                                   height=40,
                                   width=200,
                                   font=ctk.CTkFont(size=12, weight="bold"),
                                   corner_radius=8)
        btn_agregar.grid(row=3, column=0, columnspan=4, pady=20, sticky='e')
        
        # ============================================
        # 5. PANEL DERECHO (CARRITO)
        # ============================================
        right_panel = ctk.CTkFrame(main_container, corner_radius=10, fg_color="#ecf0f1")
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=10)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # Título del carrito
        carrito_header = ctk.CTkFrame(right_panel, fg_color="#2c3e50", corner_radius=8)
        carrito_header.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(carrito_header, 
                     text="🛍️ CARRITO DE COMPRA",
                     font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
                     text_color="white").pack(pady=10)
        
        # Treeview para el carrito
        tree_frame = ctk.CTkFrame(right_panel, corner_radius=8)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Configurar estilo del Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", 
                       font=('Arial', 10, 'bold'), 
                       background='#34495e', 
                       foreground='white',
                       padding=5)
        style.configure("Treeview", 
                       font=('Arial', 9), 
                       rowheight=28, 
                       background='white',
                       fieldbackground='white',
                       foreground='black')
        style.map('Treeview', 
                 background=[('selected', '#3498db')])
        
        # Crear Treeview
        self.tree_carrito = ttk.Treeview(tree_frame,
                                        columns=("tipo", "nombre", "cantidad", "precio_unitario", "subtotal"),
                                        show="headings",
                                        height=10)
        
        # Configurar columnas
        column_configs = [
            ("tipo", "TIPO", 70),
            ("nombre", "NOMBRE", 150),
            ("cantidad", "CANT.", 60),
            ("precio_unitario", "P. UNIT.", 80),
            ("subtotal", "SUBTOTAL", 80)
        ]
        
        for col_name, heading, width in column_configs:
            self.tree_carrito.heading(col_name, text=heading)
            self.tree_carrito.column(col_name, width=width, anchor="center")
        
        self.tree_carrito.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_carrito.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree_carrito.configure(yscrollcommand=v_scrollbar.set)
        
        # Panel de total y botones
        total_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        total_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 10))
        total_frame.grid_columnconfigure(1, weight=1)
        
        # Total
        ctk.CTkLabel(total_frame, 
                     text="TOTAL:", 
                     font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
                     text_color="#2c3e50").grid(row=0, column=0, padx=(0, 10), pady=8, sticky='w')
        
        self.label_total = ctk.CTkLabel(total_frame, 
                                       text="$0.00",
                                       font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
                                       text_color="#27ae60")
        self.label_total.grid(row=0, column=1, padx=10, pady=8, sticky='w')
        
        # Botones de acción
        action_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        action_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 15))
        
        btn_cancelar = ctk.CTkButton(action_frame, 
                                    text="❌ CANCELAR",
                                    command=self.limpiar_carrito,
                                    fg_color="#e74c3c",
                                    hover_color="#c0392b",
                                    height=40,
                                    width=120,
                                    font=ctk.CTkFont(size=12, weight="bold"),
                                    corner_radius=6)
        btn_cancelar.pack(side='left', padx=5)
        
        btn_pagar = ctk.CTkButton(action_frame, 
                                 text="💵 PROCESAR PAGO",
                                 command=self.procesar_pago,
                                 fg_color="#2ecc71",
                                 hover_color="#27ae60",
                                 height=40,
                                 width=160,
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 corner_radius=8)
        btn_pagar.pack(side='right', padx=5)

    def toggle_menu(self):
        """Alterna el estado del menú lateral"""
        if not self.menu_abierto:
            self.panel_menu.place(x=0, y=80)
            self.panel_menu.lift()
            self.menu_abierto = True
        else:
            self.panel_menu.place(x=-250, y=80)
            self.menu_abierto = False

    # ============================================
    # FUNCIONES DE NEGOCIO (MANTENIDAS)
    # ============================================
    
    def agregar_servicio(self, servicio):
        item_carrito = {
            'tipo': 'Servicio',
            'id': servicio['id'],
            'nombre': servicio['nombre'],
            'cantidad': 1,
            'precio_unitario': servicio['precio'],
            'subtotal': servicio['precio']
        }
        
        servicio_existente = None
        for item in self.carrito:
            if item['tipo'] == 'Servicio' and item['id'] == servicio['id']:
                servicio_existente = item
                break
        
        if servicio_existente:
            respuesta = messagebox.askyesno(
                "Servicio Existente", 
                f"El servicio '{servicio['nombre']}' ya está en el carrito.\n¿Desea agregar otro?"
            )
            if respuesta:
                self.carrito.append(item_carrito)
        else:
            self.carrito.append(item_carrito)
        
        self.actualizar_carrito()
        self.calcular_total()
        messagebox.showinfo("Servicio Agregado", f"Servicio '{servicio['nombre']}' agregado al carrito.")

    def actualizar_precio(self, producto_seleccionado):
        self.label_stock_info.configure(text="")
        
        if producto_seleccionado:
            for producto in self.productos_disponibles:
                nombre_completo = f"{producto[1]} - ${producto[3]}"
                if nombre_completo == producto_seleccionado:
                    precio = float(producto[3])
                    self.label_precio.configure(text=f"${precio:.2f}")
                    
                    stock_info = verificar_stock(producto[0], 1)
                    if stock_info:
                        color = '#2ecc71' if stock_info['stock_actual'] > 10 else '#f39c12' if stock_info['stock_actual'] > 0 else '#e74c3c'
                        self.label_stock_info.configure(
                            text=f"Stock disponible: {stock_info['stock_actual']} unidades",
                            text_color=color
                        )
                    break

    def agregar_al_carrito(self):
        producto_seleccionado = self.combo_productos.get()
        cantidad_text = self.entry_cantidad.get().strip()
        
        if not producto_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un producto.")
            return
        
        try:
            cantidad = int(cantidad_text)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Advertencia", "Ingrese una cantidad válida y mayor a 0.")
            return
        
        producto_info = None
        for producto in self.productos_disponibles:
            nombre_completo = f"{producto[1]} - ${producto[3]}"
            if nombre_completo == producto_seleccionado:
                producto_info = producto
                break
        
        if not producto_info:
            return
        
        stock_info = verificar_stock(producto_info[0], cantidad)
        
        if stock_info is None:
            messagebox.showerror("Error", "No se pudo verificar el stock del producto.")
            return
        
        if not stock_info['suficiente']:
            respuesta = messagebox.askyesno(
                "Stock Insuficiente",
                f"Solo hay {stock_info['stock_actual']} unidades disponibles de '{stock_info['nombre']}'.\n"
                f"¿Desea agregar solo {stock_info['stock_actual']} unidades al carrito?"
            )
            
            if respuesta and stock_info['stock_actual'] > 0:
                cantidad = stock_info['stock_actual']
            else:
                return
        
        producto_existente = None
        for item in self.carrito:
            if item['tipo'] == 'Producto' and item['id'] == producto_info[0]:
                producto_existente = item
                break
        
        if producto_existente:
            stock_total_necesario = producto_existente['cantidad'] + cantidad
            stock_total_info = verificar_stock(producto_info[0], stock_total_necesario)
            
            if not stock_total_info['suficiente']:
                cantidad_disponible = stock_total_info['stock_actual']
                respuesta = messagebox.askyesno(
                    "Stock Insuficiente",
                    f"Ya tiene {producto_existente['cantidad']} unidades en el carrito.\n"
                    f"Solo quedan {cantidad_disponible} unidades disponibles.\n"
                    f"¿Desea actualizar a {cantidad_disponible} unidades totales?"
                )
                if respuesta and cantidad_disponible > 0:
                    producto_existente['cantidad'] = cantidad_disponible
                    producto_existente['subtotal'] = producto_existente['cantidad'] * float(producto_info[3])
                else:
                    return
            else:
                producto_existente['cantidad'] += cantidad
                producto_existente['subtotal'] = producto_existente['cantidad'] * float(producto_info[3])
        else:
            self.carrito.append({
                'tipo': 'Producto',
                'id': producto_info[0],
                'nombre': producto_info[1],
                'cantidad': cantidad,
                'precio_unitario': float(producto_info[3]),
                'subtotal': float(producto_info[3]) * cantidad
            })
        
        self.actualizar_carrito()
        self.calcular_total()
        
        self.combo_productos.set('')
        self.label_precio.configure(text="$0.00")
        self.label_stock_info.configure(text="")
        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, "1")

    def actualizar_carrito(self):
        for row in self.tree_carrito.get_children():
            self.tree_carrito.delete(row)
        
        for item in self.carrito:
            self.tree_carrito.insert("", tk.END, values=(
                item['tipo'],
                item['nombre'],
                item['cantidad'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            ))

    def calcular_total(self):
        total = sum(item['subtotal'] for item in self.carrito)
        self.label_total.configure(text=f"${total:.2f}")

    def limpiar_carrito(self):
        if self.carrito:
            respuesta = messagebox.askyesno("Cancelar Venta", "¿Está seguro de cancelar toda la venta?")
            if respuesta:
                self.carrito = []
                self.actualizar_carrito()
                self.calcular_total()
                self.combo_productos.set('')
                self.label_precio.configure(text="$0.00")
                self.label_stock_info.configure(text="")
                self.entry_cantidad.delete(0, tk.END)
                self.entry_cantidad.insert(0, "1")

    def procesar_pago(self):
        if not self.carrito:
            messagebox.showwarning("Advertencia", "No hay productos o servicios en el carrito.")
            return
        
        total = sum(item['subtotal'] for item in self.carrito)
        
        resumen = "RESUMEN DE LA VENTA:\n\n"
        for item in self.carrito:
            resumen += f"• {item['tipo']}: {item['nombre']} x {item['cantidad']} = ${item['subtotal']:.2f}\n"
        resumen += f"\nTOTAL: ${total:.2f}"
        
        confirmar = messagebox.askyesno("Confirmar Pago", resumen)
        
        if confirmar:
            venta_id_gruppo = f"VENTA-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
            productos_stock_bajo = []
            exito = True
            
            for item in self.carrito:
                if item['tipo'] == 'Producto':
                    resultado_stock = disminuir_stock(item['id'], item['cantidad'])
                    
                    if resultado_stock.get('success'):
                        if resultado_stock.get('stock_bajo'):
                            productos_stock_bajo.append({
                                'nombre': item['nombre'],
                                'stock_actual': resultado_stock.get('nuevo_stock')
                            })
                    else:
                        messagebox.showerror("Error", f"No hay suficiente stock para {item['nombre']}")
                        exito = False
                        break
                
                if exito:
                    if item['tipo'] == 'Producto':
                        resultado = guardar_venta(
                            venta_id_gruppo,
                            self.id_usuario,
                            item['id'],
                            None,
                            item['cantidad'],
                            item['precio_unitario'],
                            item['subtotal']
                        )
                    else:
                        resultado = guardar_venta(
                            venta_id_gruppo,
                            self.id_usuario,
                            None,
                            item['nombre'],
                            item['cantidad'],
                            item['precio_unitario'],
                            item['subtotal']
                        )
                    
                    if not resultado:
                        exito = False
                
                if not exito:
                    break
            
            if exito:
                mensaje_exito = f"✅ VENTA PROCESADA EXITOSAMENTE\n\nTotal: ${total:.2f}\nID de venta: {venta_id_gruppo}"
                
                if productos_stock_bajo:
                    mensaje_stock = "\n\n⚠️ PRODUCTOS CON STOCK BAJO:\n"
                    for producto in productos_stock_bajo:
                        mensaje_stock += f"• {producto['nombre']}: {producto['stock_actual']} unidades restantes\n"
                    mensaje_exito += mensaje_stock
                
                messagebox.showinfo("Éxito", mensaje_exito)
                self.limpiar_carrito()
                self.ver_productos()
            else:
                messagebox.showerror("Error", "No se pudo completar la venta.")

    def ver_productos(self):
        try:
            self.productos_disponibles = ver_producto()
            
            if not self.productos_disponibles:
                self.combo_productos.configure(values=[])
                return
            
            productos_formato = []
            for producto in self.productos_disponibles:
                if len(producto) >= 4:
                    nombre = producto[1] if producto[1] else "Sin nombre"
                    precio = producto[3] if producto[3] else 0
                    productos_formato.append(f"{nombre} - ${precio}")
            
            self.combo_productos.configure(values=productos_formato)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {str(e)}")

    def gestionar_servicios(self):
        self.root.withdraw()
        root = ctk.CTkToplevel(self.root)
        ServiciosView(root, self)
        root.mainloop()

    def gestionar_productos(self):
        self.root.withdraw()
        root = ctk.CTkToplevel(self.root)
        Stockview(root, self)
        root.mainloop()

    def history_product(self):
        """Abre la vista de historial de ventas"""
        try:
            # Usar la función optimizada para evitar importación circular
            from historial_viw import abrir_historial_desde_punto_venta
            
            # Ocultar ventana actual
            self.root.withdraw()
            
            # Llamar a la función optimizada
            app = abrir_historial_desde_punto_venta(
                parent_window=self,
                username=self.username,
                tipo_usuario=self.tipo_usuario,
                id_usuario=self.id_usuario
            )
            
            if app:
                # Configurar comportamiento al cerrar
                app.root.protocol("WM_DELETE_WINDOW", lambda: self.on_historial_close(app))
            else:
                # Si hay error, mostrar ventana principal
                self.root.deiconify()
                
        except Exception as e:
            print(f"Error al abrir historial: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el historial:\n{str(e)}")
            self.root.deiconify()

    def on_historial_close(self, historial_app):
        """Maneja el cierre de la ventana de historial"""
        try:
            if hasattr(historial_app, 'cerrar_ventana'):
                historial_app.cerrar_ventana()
            elif hasattr(historial_app, 'root'):
                historial_app.root.destroy()
        finally:
            # Mostrar ventana principal
            self.root.deiconify()

    def abrir_user_view(self):
        self.root.withdraw()
        root = ctk.CTkToplevel(self.root)
        UsuariosView(root, self.username, self)
        root.mainloop()

    def salir_sistema(self):
        if messagebox.askyesno("Salir del Sistema", "¿Está seguro de que desea salir completamente del sistema?"):
            self.root.quit()
            self.root.destroy()

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro de que desea cerrar sesión?"):
            self.root.destroy()
            from login_viw import loginapp
            root = tk.Tk()
            app = loginapp(root)
            root.mainloop()

if __name__ == "__main__":
    app2 = UserApp2("admin")