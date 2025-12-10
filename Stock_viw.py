import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from Stock_controller import (
    obtener_productos, obtener_producto_por_id, obtener_productos_stock_bajo,
    agregar_producto, actualizar_producto, actualizar_stock, incrementar_stock,
    eliminar_producto, buscar_productos
)

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def cargar_imagen(ruta, tamaño=(60, 60)):
    """Carga y redimensiona una imagen"""
    try:
        img = Image.open(ruta)
        img = img.resize(tamaño, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=tamaño)
    except Exception as e:
        print(f"Error al cargar imagen: {e}")
        return None

class Stockview:
    def __init__(self, root, user_app_ref=None):
        self.root = root
        self.user_app_ref = user_app_ref
        self.root.title("Gestión de Stock - Barbería Bravo")
        
        # Configurar ventana
        self.root.geometry("1200x700")
        self.centrar_ventana(self.root, 1200, 700)
        
        # Variables
        self.buscar_var = tk.StringVar()
        self.menu_abierto = False
        self.logo = cargar_imagen("c9141f85-d013-448a-aea0-2201255befd4.jpg")
        
        self.crear_interfaz()
        self.actualizar_lista()
    
    def centrar_ventana(self, ventana, ancho, alto):
        """Centra una ventana en la pantalla"""
        ventana.update_idletasks()
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def crear_interfaz(self):
        # ============================================
        # 1. HEADER SUPERIOR
        # ============================================
        header_frame = ctk.CTkFrame(self.root, height=70, corner_radius=0, fg_color="#1a1a1a")
        header_frame.pack(fill='x', side='top')
        
        # Logo y título
        if self.logo:
            ctk.CTkLabel(header_frame, image=self.logo, text="", fg_color="#1a1a1a").pack(side='left', padx=(20, 10), pady=5)
        
        ctk.CTkLabel(
            header_frame, 
            text="📦 GESTIÓN DE STOCK",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="white"
        ).pack(side='left', padx=10, pady=10)
        
        # Botón hamburguesa
        self.btn_hamburguesa = ctk.CTkButton(
            header_frame, 
            text="☰ Menú", 
            width=90, 
            height=30,
            command=self.toggle_menu,
            fg_color="#3498db", 
            hover_color="#2980b9",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_hamburguesa.pack(side='right', padx=(0, 10), pady=10)
        
        # ============================================
        # 2. PANEL DE MENÚ LATERAL
        # ============================================
        self.panel_menu = ctk.CTkFrame(self.root, width=220, corner_radius=0, fg_color="#2c3e50")
        self.panel_menu.place(x=-220, y=70, relheight=1)
        
        opciones = [
            ("📦 Volver a Punto de Venta", self.volver_punto_venta),
            ("📊 Stock Bajo", self.mostrar_stock_bajo),
            ("➕ Agregar Producto", self.mostrar_agregar_producto),
            ("🔄 Actualizar Lista", self.actualizar_lista),
            ("🔄 Cerrar Sesión", self.cerrar_sesion),
            ("✖️ Salir Sistema", self.salir_sistema)
        ]
        
        for i, (texto, comando) in enumerate(opciones):
            btn = ctk.CTkButton(
                self.panel_menu, 
                text=texto, 
                command=lambda cmd=comando: [self.toggle_menu(), cmd()],
                fg_color="transparent", 
                hover_color="#34495e", 
                text_color="white",
                font=ctk.CTkFont(family="Arial", size=12),
                anchor='w', 
                height=40, 
                width=200
            )
            btn.place(x=10, y=20 + i*45)
        
        # ============================================
        # 3. CONTENIDO PRINCIPAL
        # ============================================
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill='both', expand=True, padx=0, pady=0)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # ============================================
        # 4. BARRA DE BÚSQUEDA
        # ============================================
        buscar_frame = ctk.CTkFrame(main_container, corner_radius=8)
        buscar_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=8)
        buscar_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(buscar_frame, text="🔍 Buscar:", font=ctk.CTkFont(size=11)).grid(
            row=0, column=0, padx=(10, 5), pady=8)
        
        self.entry_buscar = ctk.CTkEntry(
            buscar_frame, 
            textvariable=self.buscar_var,
            placeholder_text="Nombre o proveedor...",
            font=ctk.CTkFont(size=11),
            height=32
        )
        self.entry_buscar.grid(row=0, column=1, padx=5, pady=8, sticky='ew')
        
        btn_buscar = ctk.CTkButton(
            buscar_frame, 
            text="BUSCAR", 
            command=self.buscar_productos,
            fg_color="#3498db", 
            hover_color="#2980b9",
            width=100, 
            height=32,
            font=ctk.CTkFont(size=11)
        )
        btn_buscar.grid(row=0, column=2, padx=5, pady=8)
        
        btn_mostrar = ctk.CTkButton(
            buscar_frame, 
            text="MOSTRAR TODOS", 
            command=self.actualizar_lista,
            fg_color="#f39c12", 
            hover_color="#d68910",
            width=120, 
            height=32,
            font=ctk.CTkFont(size=11)
        )
        btn_mostrar.grid(row=0, column=3, padx=(5, 10), pady=8)
        
        # ============================================
        # 5. LISTA DE PRODUCTOS (TREEVIEW)
        # ============================================
        tree_frame = ctk.CTkFrame(main_container, corner_radius=8)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 8))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Configurar estilo del Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", 
                       font=('Arial', 10, 'bold'), 
                       background='#34495e', 
                       foreground='white',
                       padding=4)
        style.configure("Treeview", 
                       font=('Arial', 9), 
                       rowheight=28,
                       background='white', 
                       fieldbackground='white',
                       foreground='black')
        
        # Crear Treeview
        columns = ('ID', 'Nombre', 'Stock', 'Precio', 'Proveedor')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        column_configs = [
            ('ID', 50, 'center'),
            ('Nombre', 280, 'w'),
            ('Stock', 90, 'center'),
            ('Precio', 90, 'center'),
            ('Proveedor', 180, 'w')
        ]
        
        for col, width, anchor in column_configs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, columnspan=2, sticky='ew')
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.entry_buscar.bind('<Return>', lambda e: self.buscar_productos())
        
        # ============================================
        # 6. BOTONES DE ACCIÓN
        # ============================================
        action_frame = ctk.CTkFrame(main_container, corner_radius=8)
        action_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 10))
        
        botones_principales = [
            ("➕ AGREGAR", self.mostrar_agregar_producto, '#2ecc71'),
            ("✏️ EDITAR", self.mostrar_editar_producto, '#3498db'),
            ("🗑️ ELIMINAR", self.mostrar_eliminar_producto, '#e74c3c'),
            ("📈 AGREGAR STOCK", self.mostrar_agregar_stock, '#f39c12'),
            ("⚠️ STOCK BAJO", self.mostrar_stock_bajo, '#f1c40f'),
            ("🔄 ACTUALIZAR", self.actualizar_lista, '#9b59b6')
        ]
        
        for i, (texto, comando, color) in enumerate(botones_principales):
            btn = ctk.CTkButton(
                action_frame, 
                text=texto, 
                command=comando,
                fg_color=color, 
                hover_color=self.oscurecer_color(color),
                height=35, 
                width=140,
                font=ctk.CTkFont(size=11),
                corner_radius=5
            )
            btn.grid(row=0, column=i, padx=3, pady=5)
            action_frame.grid_columnconfigure(i, weight=1)
    
    def oscurecer_color(self, color):
        """Oscurece un color para el efecto hover"""
        colores = {
            '#2ecc71': '#27ae60',
            '#3498db': '#2980b9',
            '#e74c3c': '#c0392b',
            '#f39c12': '#d68910',
            '#f1c40f': '#f39c12',
            '#9b59b6': '#8e44ad'
        }
        return colores.get(color, color)
    
    def toggle_menu(self):
        """Alterna el estado del menú lateral"""
        if not self.menu_abierto:
            self.panel_menu.place(x=0, y=70)
            self.panel_menu.lift()
            self.menu_abierto = True
        else:
            self.panel_menu.place(x=-220, y=70)
            self.menu_abierto = False
    
    # ============================================
    # MÉTODOS DE GESTIÓN DE PRODUCTOS
    # ============================================
    
    def actualizar_lista(self):
        """Actualiza la lista de productos"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        productos = obtener_productos()
        for producto in productos:
            self.tree.insert('', tk.END, values=(
                producto['id_producto'],
                producto['nombre_producto'],
                producto['stock'],
                f"${producto['precio']:.2f}",
                producto['proveedor']
            ))
    
    def buscar_productos(self):
        """Busca productos según el término ingresado"""
        termino = self.buscar_var.get().strip()
        if not termino:
            self.actualizar_lista()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        productos = buscar_productos(termino)
        for producto in productos:
            self.tree.insert('', tk.END, values=(
                producto['id_producto'],
                producto['nombre_producto'],
                producto['stock'],
                f"${producto['precio']:.2f}",
                producto['proveedor']
            ))
    
    def on_double_click(self, event):
        """Al hacer doble click en un producto, lo edita"""
        self.mostrar_editar_producto()
    
    # ============================================
    # VENTANAS DE FORMULARIO - AGREGAR PRODUCTO
    # ============================================
    
    def mostrar_agregar_producto(self):
        """Muestra el formulario para agregar nuevo producto"""
        # Crear ventana
        self.ventana_agregar = ctk.CTkToplevel(self.root)
        self.ventana_agregar.title("➕ Agregar Producto")
        self.ventana_agregar.geometry("500x500")
        self.ventana_agregar.transient(self.root)
        self.ventana_agregar.grab_set()
        self.centrar_ventana(self.ventana_agregar, 500, 500)
        
        # Hacer que la ventana esté por encima
        self.ventana_agregar.lift()
        self.ventana_agregar.focus_force()
        
        # Frame principal
        frame = ctk.CTkFrame(self.ventana_agregar, corner_radius=10)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            frame, 
            text="➕ AGREGAR NUEVO PRODUCTO", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))
        
        # Campos del formulario
        campos = [
            ("Nombre del Producto:", "nombre"),
            ("Stock Inicial:", "stock"),
            ("Precio ($):", "precio"),
            ("Proveedor:", "proveedor")
        ]
        
        self.entries = {}
        
        for i, (label, key) in enumerate(campos):
            # Frame para cada campo
            campo_frame = ctk.CTkFrame(frame, fg_color="transparent")
            campo_frame.pack(fill='x', padx=10, pady=8)
            
            # Label
            ctk.CTkLabel(
                campo_frame, 
                text=label, 
                font=ctk.CTkFont(size=14, weight="bold"),
                width=150
            ).pack(side='left', padx=(0, 10))
            
            # Entry
            if key == "stock":
                entry = ctk.CTkEntry(
                    campo_frame, 
                    placeholder_text="Ej: 10",
                    font=ctk.CTkFont(size=14),
                    height=40,
                    width=250
                )
                entry.insert(0, "0")
            elif key == "precio":
                entry = ctk.CTkEntry(
                    campo_frame, 
                    placeholder_text="Ej: 25.00",
                    font=ctk.CTkFont(size=14),
                    height=40,
                    width=250
                )
                entry.insert(0, "0.00")
            else:
                entry = ctk.CTkEntry(
                    campo_frame, 
                    placeholder_text=f"Ingrese {label.lower()}",
                    font=ctk.CTkFont(size=14),
                    height=40,
                    width=250
                )
            
            entry.pack(side='left', fill='x', expand=True)
            self.entries[key] = entry
        
        # Separador
        ctk.CTkFrame(frame, height=2, fg_color="#34495e").pack(fill='x', pady=20)
        
        # Frame para botones
        botones_frame = ctk.CTkFrame(frame, fg_color="transparent")
        botones_frame.pack(pady=10)
        
        # Botón Agregar
        btn_agregar = ctk.CTkButton(
            botones_frame,
            text="➕ AGREGAR PRODUCTO",
            command=self.agregar_producto,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=45,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8
        )
        btn_agregar.pack(side='left', padx=10)
        
        # Botón Cancelar
        btn_cancelar = ctk.CTkButton(
            botones_frame,
            text="❌ CANCELAR",
            command=self.ventana_agregar.destroy,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=45,
            width=120,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8
        )
        btn_cancelar.pack(side='left', padx=10)
        
        # Enfocar el primer campo
        self.entries['nombre'].focus()
        
        # DEBUG: Para verificar que la ventana se creó
        print("✅ Ventana de agregar producto creada")
    
    def agregar_producto(self):
        """Procesa el formulario de agregar producto"""
        # Obtener valores
        nombre = self.entries['nombre'].get().strip()
        stock = self.entries['stock'].get().strip()
        precio = self.entries['precio'].get().strip()
        proveedor = self.entries['proveedor'].get().strip()
        
        # Validar campos
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre del producto es obligatorio")
            self.entries['nombre'].focus()
            return
        
        if not proveedor:
            messagebox.showwarning("Advertencia", "El proveedor es obligatorio")
            self.entries['proveedor'].focus()
            return
        
        # Validar stock
        try:
            stock_int = int(stock)
            if stock_int < 0:
                messagebox.showwarning("Advertencia", "El stock no puede ser negativo")
                self.entries['stock'].focus()
                return
        except ValueError:
            messagebox.showerror("Error", "El stock debe ser un número entero válido")
            self.entries['stock'].focus()
            return
        
        # Validar precio
        try:
            precio_float = float(precio)
            if precio_float < 0:
                messagebox.showwarning("Advertencia", "El precio no puede ser negativo")
                self.entries['precio'].focus()
                return
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido (ej: 25.00)")
            self.entries['precio'].focus()
            return
        
        # Intentar agregar el producto
        try:
            print(f"Intentando agregar producto: {nombre}, {stock_int}, {precio_float}, {proveedor}")
            if agregar_producto(nombre, stock_int, precio_float, proveedor):
                messagebox.showinfo("Éxito", "✅ Producto agregado correctamente")
                self.ventana_agregar.destroy()
                self.actualizar_lista()
            else:
                messagebox.showerror("Error", "❌ No se pudo agregar el producto. Verifique la conexión a la base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al agregar producto: {str(e)}")
            print(f"Error detallado: {e}")
    
    def mostrar_editar_producto(self):
        """Ventana para editar producto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
        
        item = self.tree.item(seleccion[0])
        id_producto = item['values'][0]
        
        # Obtener datos del producto
        producto = obtener_producto_por_id(id_producto)
        if not producto:
            messagebox.showerror("Error", "No se pudo obtener la información del producto")
            return
        
        # Crear ventana de edición
        self.ventana_editar = ctk.CTkToplevel(self.root)
        self.ventana_editar.title("✏️ Editar Producto")
        self.ventana_editar.geometry("500x500")
        self.ventana_editar.transient(self.root)
        self.ventana_editar.grab_set()
        self.centrar_ventana(self.ventana_editar, 500, 500)
        
        # Frame principal
        frame = ctk.CTkFrame(self.ventana_editar, corner_radius=10)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            frame, 
            text="✏️ EDITAR PRODUCTO", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))
        
        # Campos del formulario
        campos = [
            ("Nombre del Producto:", "nombre", producto['nombre_producto']),
            ("Stock:", "stock", str(producto['stock'])),
            ("Precio ($):", "precio", str(producto['precio'])),
            ("Proveedor:", "proveedor", producto['proveedor'])
        ]
        
        self.entries_editar = {}
        
        for i, (label, key, valor) in enumerate(campos):
            # Frame para cada campo
            campo_frame = ctk.CTkFrame(frame, fg_color="transparent")
            campo_frame.pack(fill='x', padx=10, pady=8)
            
            # Label
            ctk.CTkLabel(
                campo_frame, 
                text=label, 
                font=ctk.CTkFont(size=14, weight="bold"),
                width=150
            ).pack(side='left', padx=(0, 10))
            
            # Entry
            entry = ctk.CTkEntry(
                campo_frame, 
                font=ctk.CTkFont(size=14),
                height=40,
                width=250
            )
            entry.insert(0, valor)
            entry.pack(side='left', fill='x', expand=True)
            self.entries_editar[key] = entry
        
        # Separador
        ctk.CTkFrame(frame, height=2, fg_color="#34495e").pack(fill='x', pady=20)
        
        # Frame para botones
        botones_frame = ctk.CTkFrame(frame, fg_color="transparent")
        botones_frame.pack(pady=10)
        
        # Botón Guardar
        btn_guardar = ctk.CTkButton(
            botones_frame,
            text="💾 GUARDAR CAMBIOS",
            command=lambda: self.guardar_edicion_producto(id_producto),
            fg_color="#3498db",
            hover_color="#2980b9",
            height=45,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8
        )
        btn_guardar.pack(side='left', padx=10)
        
        # Botón Cancelar
        btn_cancelar = ctk.CTkButton(
            botones_frame,
            text="❌ CANCELAR",
            command=self.ventana_editar.destroy,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=45,
            width=120,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8
        )
        btn_cancelar.pack(side='left', padx=10)
        
        # Enfocar el primer campo
        self.entries_editar['nombre'].focus()
    
    def guardar_edicion_producto(self, id_producto):
        """Guarda los cambios de un producto editado"""
        # Obtener valores
        nombre = self.entries_editar['nombre'].get().strip()
        stock = self.entries_editar['stock'].get().strip()
        precio = self.entries_editar['precio'].get().strip()
        proveedor = self.entries_editar['proveedor'].get().strip()
        
        # Validaciones
        if not nombre or not proveedor:
            messagebox.showwarning("Advertencia", "Nombre y proveedor son obligatorios")
            return
        
        try:
            stock_int = int(stock)
            precio_float = float(precio)
            
            if stock_int < 0 or precio_float < 0:
                messagebox.showwarning("Advertencia", "Stock y precio no pueden ser negativos")
                return
            
            if actualizar_producto(id_producto, nombre, stock_int, precio_float, proveedor):
                messagebox.showinfo("Éxito", "✅ Producto actualizado correctamente")
                self.ventana_editar.destroy()
                self.actualizar_lista()
            else:
                messagebox.showerror("Error", "❌ No se pudo actualizar el producto")
        except ValueError:
            messagebox.showerror("Error", "❌ Stock debe ser un número entero y precio un número válido")
    
    def mostrar_eliminar_producto(self):
        """Elimina el producto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        item = self.tree.item(seleccion[0])
        id_producto = item['values'][0]
        nombre_producto = item['values'][1]
        
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Está seguro de eliminar el producto:\n{nombre_producto}?\n\nEsta acción no se puede deshacer."
        )
        
        if respuesta:
            if eliminar_producto(id_producto):
                messagebox.showinfo("Éxito", "✅ Producto eliminado correctamente")
                self.actualizar_lista()
            else:
                messagebox.showerror("Error", "❌ No se pudo eliminar el producto")
    
    def mostrar_agregar_stock(self):
        """Ventana para AGREGAR stock al producto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = self.tree.item(seleccion[0])
        id_producto = item['values'][0]
        nombre_producto = item['values'][1]
        stock_actual = int(item['values'][2])
        
        self.ventana_stock = ctk.CTkToplevel(self.root)
        self.ventana_stock.title("📈 Agregar Stock")
        self.ventana_stock.geometry("400x350")
        self.ventana_stock.transient(self.root)
        self.ventana_stock.grab_set()
        self.centrar_ventana(self.ventana_stock, 400, 350)
        
        frame = ctk.CTkFrame(self.ventana_stock, corner_radius=8)
        frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Título
        ctk.CTkLabel(frame, text="📈 AGREGAR STOCK", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        
        # Información del producto
        ctk.CTkLabel(frame, text=f"Producto: {nombre_producto}", font=ctk.CTkFont(size=12)).pack(pady=5)
        ctk.CTkLabel(frame, text=f"Stock actual: {stock_actual}", font=ctk.CTkFont(size=12, weight="bold"), 
                    text_color="#27ae60").pack(pady=5)
        
        ctk.CTkFrame(frame, height=1, fg_color="#bdc3c7").pack(fill='x', pady=10)
        
        # Campo de entrada
        ctk.CTkLabel(frame, text="Cantidad a sumar:", font=ctk.CTkFont(size=11)).pack(pady=5)
        
        self.cantidad_var = tk.StringVar(value="")
        entry_cantidad = ctk.CTkEntry(
            frame, 
            textvariable=self.cantidad_var,
            font=ctk.CTkFont(size=12),
            height=35, 
            width=100,
            justify='center'
        )
        entry_cantidad.pack(pady=5)
        entry_cantidad.focus()
        
        # Botones
        botones_frame = ctk.CTkFrame(frame, fg_color="transparent")
        botones_frame.pack(pady=20)
        
        btn_agregar = ctk.CTkButton(
            botones_frame,
            text="📈 AGREGAR",
            command=lambda: self.guardar_stock_incrementado(
                id_producto, 
                self.cantidad_var.get(), 
                nombre_producto
            ),
            fg_color="#27ae60", 
            hover_color="#219653",
            height=35, 
            width=120,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        btn_agregar.pack(side='left', padx=5)
        
        btn_cancelar = ctk.CTkButton(
            botones_frame,
            text="❌ CANCELAR",
            command=self.ventana_stock.destroy,
            fg_color="#95a5a6", 
            hover_color="#7f8c8d",
            height=35, 
            width=100,
            font=ctk.CTkFont(size=11)
        )
        btn_cancelar.pack(side='left', padx=5)
    
    def guardar_stock_incrementado(self, id_producto, cantidad, nombre_producto):
        """Guarda el stock INCREMENTADO"""
        try:
            if not cantidad:
                messagebox.showwarning("Advertencia", "Ingrese una cantidad")
                return
            
            cantidad_int = int(cantidad)
            if cantidad_int <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                return
            
            if incrementar_stock(id_producto, cantidad_int):
                messagebox.showinfo("Éxito", f"✅ Se agregaron {cantidad_int} unidades")
                self.ventana_stock.destroy()
                self.actualizar_lista()
                
                # Verificar stock bajo después de agregar
                producto = obtener_producto_por_id(id_producto)
                if producto and producto['stock'] <= 5:
                    messagebox.showwarning(
                        "Stock Bajo", 
                        f"⚠️ {nombre_producto} todavía tiene stock bajo: {producto['stock']} unidades"
                    )
            else:
                messagebox.showerror("Error", "❌ No se pudo actualizar el stock")
        except ValueError:
            messagebox.showerror("Error", "❌ La cantidad debe ser un número válido")
    
    def mostrar_stock_bajo(self):
        """Muestra solo los productos con stock bajo"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        productos = obtener_productos_stock_bajo()
        if not productos:
            messagebox.showinfo("Stock Bajo", "✅ No hay productos con stock bajo")
            self.actualizar_lista()
            return
        
        # Contar productos
        contador_bajo = len(productos)
        productos_criticos = [p for p in productos if p['stock'] <= 2]
        
        for producto in productos:
            nombre = producto['nombre_producto']
            if producto['stock'] <= 2:
                nombre = f"{nombre} ⚠️"
            
            self.tree.insert('', tk.END, values=(
                producto['id_producto'],
                nombre,
                producto['stock'],
                f"${producto['precio']:.2f}",
                producto['proveedor']
            ))
        
        # Mostrar resumen
        mensaje = f"📊 Productos con stock bajo: {contador_bajo}"
        if productos_criticos:
            mensaje += f"\n\n⚠️ Críticos (≤ 2 unidades): {len(productos_criticos)}"
            for p in productos_criticos[:3]:
                mensaje += f"\n• {p['nombre_producto']}: {p['stock']} unidades"
            if len(productos_criticos) > 3:
                mensaje += f"\n... y {len(productos_criticos) - 3} más"
        
        messagebox.showinfo("Stock Bajo", mensaje)
    
    # ============================================
    # MÉTODOS DE NAVEGACIÓN
    # ============================================
    
    def volver_punto_venta(self):
        """Regresa al punto de venta principal"""
        self.root.destroy()
        if self.user_app_ref:
            self.user_app_ref.volver_al_punto_venta()
    
    def cerrar_sesion(self):
        """Cierra sesión"""
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro de cerrar sesión?"):
            self.root.destroy()
    
    def salir_sistema(self):
        """Cierra completamente la aplicación"""
        if messagebox.askyesno("Salir", "¿Está seguro de salir del sistema?"):
            self.root.quit()

if __name__ == "__main__":
    root = ctk.CTk()
    app = Stockview(root)
    root.mainloop()