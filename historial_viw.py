# historial_view.py
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import os
from PIL import Image, ImageTk
from dateutil.relativedelta import relativedelta

# Importar controladores del historial
from historial_controller import (
    obtener_ventas_agrupadas, 
    obtener_ventas_agrupadas_por_usuario,
    obtener_detalles_venta,
    obtener_estadisticas_ventas,
    obtener_estadisticas_usuario,
    obtener_ventas_por_rango_fechas
)

def cargar_imagen(ruta, tamaño=(80, 80)):
    """Carga y redimensiona una imagen"""
    try:
        img = Image.open(ruta)
        img = img.resize(tamaño, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=tamaño)
    except Exception as e:
        print(f"Error al cargar imagen: {e}")
        return None

# ============================================
# FUNCIÓN PÚBLICA PARA ABRIR DESDE PUNTO DE VENTA
# ============================================
def abrir_historial_desde_punto_venta(parent_window, username, tipo_usuario, id_usuario):
    """
    Función puente para abrir HistorialView desde UserApp2
    
    Args:
        parent_window: Instancia de UserApp2
        username: Nombre de usuario
        tipo_usuario: Tipo de usuario
        id_usuario: ID del usuario
    
    Returns:
        Instancia de HistorialView o None si hay error
    """
    try:
        historial_app = HistorialView(
            username=username,
            tipo_usuario=tipo_usuario,
            id_usuario=id_usuario,
            parent=parent_window
        )
        return historial_app
    except Exception as e:
        print(f"Error al abrir historial: {e}")
        messagebox.showerror("Error", f"No se pudo abrir el historial:\n{str(e)}")
        return None

class HistorialView:
    def __init__(self, username, tipo_usuario, id_usuario=None, parent=None):
        """
        Args:
            username: Nombre de usuario
            tipo_usuario: 'jefe' o 'trabajador'
            id_usuario: ID del usuario en la base de datos
            parent: Referencia a la ventana padre (UserApp2)
        """
        self.username = username
        self.tipo_usuario = tipo_usuario
        self.id_usuario = id_usuario
        self.parent = parent  # Referencia a UserApp2
        
        self.root = ctk.CTkToplevel()
        self.menu_abierto = True  # Iniciar con menú abierto
        self.logo = cargar_imagen("c9141f85-d013-448a-aea0-2201255befd4.jpg", tamaño=(70, 70))  # Logo más grande
        self.ventanas_secundarias = []  # Lista para mantener referencia a ventanas secundarias

        self.root.title("📊 Historial de Ventas - Barbería Bravo")
        
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
        
        # Configurar el cierre de ventana para volver a UserApp2
        if self.parent:
            self.root.protocol("WM_DELETE_WINDOW", self.cerrar_y_volver)
        
        self.crear_interfaz()
        self.cargar_ventas()
        self.root.focus_set()  # Poner foco en esta ventana
    
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
                     text="📊 HISTORIAL GENERAL DE VENTAS - BARBERÍA BRAVO", 
                     font=ctk.CTkFont(family="Arial", size=24, weight="bold"),  # Fuente más grande
                     text_color="white").pack(side='left', padx=10, pady=15)
        
        # Información del usuario (más grande)
        user_info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        user_info_frame.pack(side='right', padx=30, pady=15)
        
        tipo_texto = "👑 Jefe" if self.tipo_usuario == 'jefe' else "👨‍💼 Trabajador"
        ctk.CTkLabel(user_info_frame, 
                     text=f"👤 {self.username} | {tipo_texto}", 
                     font=ctk.CTkFont(size=14, weight="bold"),  # Fuente más grande
                     text_color="#cccccc").pack(side='top', anchor='e')
        
        # Botones de control (más grandes)
        control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        control_frame.pack(side='right', padx=(0, 20), pady=15)
        
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
                                    text="📄 EXPORTAR REPORTE",
                                    command=self.exportar_reporte,
                                    fg_color="#2ecc71",
                                    hover_color="#27ae60",
                                    width=180,  # Más ancho
                                    height=40,  # Más alto
                                    font=ctk.CTkFont(size=13, weight="bold"))
        btn_exportar.pack(side='left', padx=8)
        
        # Botón hamburguesa (más grande y con texto)
        self.btn_hamburguesa = ctk.CTkButton(header_frame, 
                                            text="☰ MENÚ PRINCIPAL", 
                                            width=140,  # Más ancho
                                            height=40,  # Más alto
                                            command=self.toggle_menu,
                                            fg_color="#555555",
                                            hover_color="#777777",
                                            font=ctk.CTkFont(size=13, weight="bold"))  # Fuente más grande
        self.btn_hamburguesa.pack(side='right', padx=(0, 20), pady=15)
        
        # ============================================
        # 2. PANEL DE MENÚ LATERAL (MÁS ANCHO Y AL FRENTE)
        # ============================================
        self.panel_menu = ctk.CTkFrame(self.root, width=280, corner_radius=0, fg_color="#2c3e50")  # Más ancho
        # COLOCAR MÁS ADELANTE (visible al inicio)
        self.panel_menu.place(x=0, y=100, relheight=1)
        self.panel_menu.lift()  # Traer al frente
        
        # Botón para cerrar el menú (en la parte superior derecha del menú)
        btn_cerrar_menu = ctk.CTkButton(self.panel_menu,
                                      text="✕",
                                      command=self.toggle_menu,
                                      fg_color="transparent",
                                      hover_color="#e74c3c",
                                      width=40,
                                      height=40,
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      text_color="white")
        btn_cerrar_menu.place(x=230, y=10)
        
        # Opciones del menú con las nuevas funciones
        opciones = [
            ("🔄 ACTUALIZAR LISTA", self.cargar_ventas),
            ("📈 VER ESTADÍSTICAS DETALLADAS", self.mostrar_estadisticas_detalladas),
            ("📋 VER DETALLES DE VENTA", self.mostrar_detalles_seleccionados),
            ("📊 VENTAS POR DÍA", self.mostrar_ventas_dia),
            ("📅 VENTAS POR SEMANA", self.mostrar_ventas_semana),
            ("🗓️ VENTAS POR MES", self.mostrar_ventas_mes),
            ("👥 APARTARSE POR DÍA", self.mostrar_apartado_dia),
            ("🔍 FILTRAR POR USUARIO", self.focus_filtro_usuario),
            ("📄 EXPORTAR REPORTE PDF", self.exportar_reporte),
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
                              width=260)  # Más ancho
            btn.place(x=10, y=60 + i*55)  # Más espacio entre botones
        
        # ============================================
        # 3. CONTENIDO PRINCIPAL
        # ============================================
        main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)  # Más padding
        
        # ============================================
        # 4. FRAME DE ESTADÍSTICAS (MÁS GRANDE)
        # ============================================
        stats_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#2c3e50")  # Más redondeado
        stats_frame.pack(fill='x', pady=(0, 15))
        
        # Estadísticas en una fila con mejor diseño
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(fill='x', padx=20, pady=15)
        
        self.label_total_ventas = ctk.CTkLabel(stats_container, 
                                              text="📊 Total de ventas: 0",
                                              font=ctk.CTkFont(size=14, weight="bold"),  # Más grande
                                              text_color="white")
        self.label_total_ventas.pack(side='left', padx=25, pady=5)
        
        self.label_monto_total = ctk.CTkLabel(stats_container, 
                                             text="💰 Monto total: $0.00",
                                             font=ctk.CTkFont(size=14, weight="bold"),
                                             text_color="#4ecdc4")
        self.label_monto_total.pack(side='left', padx=25, pady=5)
        
        self.label_total_productos = ctk.CTkLabel(stats_container, 
                                                 text="🛒 Productos vendidos: 0",
                                                 font=ctk.CTkFont(size=14, weight="bold"),
                                             text_color="#e76f51")
        self.label_total_productos.pack(side='left', padx=25, pady=5)
        
        # ============================================
        # 5. FRAME DE FILTROS (solo para jefes) 
        # ============================================
        if self.tipo_usuario == 'jefe':
            filtros_frame = ctk.CTkFrame(main_frame, corner_radius=12)
            filtros_frame.pack(fill='x', pady=(0, 15))
            
            filtros_header = ctk.CTkFrame(filtros_frame, fg_color="transparent")
            filtros_header.pack(fill='x', padx=20, pady=(15, 10))
            
            ctk.CTkLabel(filtros_header, 
                        text="🔍 FILTRAR VENTAS",
                        font=ctk.CTkFont(size=15, weight="bold"),  # Más grande
                        text_color="#2c3e50").pack(side='left', padx=(0, 20))
            
            ctk.CTkLabel(filtros_header, 
                        text="Filtrar por usuario:",
                        font=ctk.CTkFont(size=13)).pack(side='left', padx=(0, 10))
            
            self.filtro_usuario = ctk.CTkEntry(filtros_header, 
                                              placeholder_text="Ingrese nombre de usuario...",
                                              font=ctk.CTkFont(size=13),  # Más grande
                                              height=40,  # Más alto
                                              width=250)  # Más ancho
            self.filtro_usuario.pack(side='left', padx=10)
            
            btn_filtrar = ctk.CTkButton(filtros_header,
                                       text="🔍 FILTRAR",
                                       command=self.aplicar_filtro,
                                       fg_color="#45b7d1",
                                       hover_color="#3aa1c9",
                                       height=40,  # Más alto
                                       width=120,  # Más ancho
                                       font=ctk.CTkFont(size=13, weight="bold"))
            btn_filtrar.pack(side='left', padx=10)
            
            btn_limpiar = ctk.CTkButton(filtros_header,
                                       text="🔄 MOSTRAR TODAS",
                                       command=self.cargar_ventas,
                                       fg_color="#96ceb4",
                                       hover_color="#87bda2",
                                       height=40,
                                       width=150,
                                       font=ctk.CTkFont(size=13, weight="bold"))
            btn_limpiar.pack(side='left', padx=10)
        
        # ============================================
        # 6. TABLA DE VENTAS AGRUPADAS 
        # ============================================
        tabla_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        tabla_frame.pack(fill='both', expand=True, pady=(0, 15))
        tabla_frame.grid_columnconfigure(0, weight=1)
        tabla_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(tabla_frame, 
                     text="📋 VENTAS REGISTRADAS", 
                     font=ctk.CTkFont(family="Arial", size=18, weight="bold"),  # Más grande
                     text_color="#2c3e50").grid(row=0, column=0, pady=(20, 15), padx=25, sticky='w')
        
        # Frame para treeview
        tree_container = ctk.CTkFrame(tabla_frame)
        tree_container.grid(row=1, column=0, sticky='nsew', padx=25, pady=(0, 15))
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
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
        
        # Configurar columnas según el tipo de usuario (más anchas)
        if self.tipo_usuario == 'jefe':
            columns = ("grupo", "usuario", "items", "total", "fecha")
            self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=16)  # Más alto
            
            self.tree.heading("grupo", text="ID VENTA")
            self.tree.heading("usuario", text="USUARIO")
            self.tree.heading("items", text="ITEMS")
            self.tree.heading("total", text="TOTAL ($)")
            self.tree.heading("fecha", text="FECHA Y HORA")
            
            self.tree.column("grupo", width=150, anchor="center")  # Más ancho
            self.tree.column("usuario", width=150, anchor="center")  # Más ancho
            self.tree.column("items", width=100, anchor="center")  # Más ancho
            self.tree.column("total", width=120, anchor="center")  # Más ancho
            self.tree.column("fecha", width=180, anchor="center")  # Más ancho
        else:
            columns = ("grupo", "items", "total", "fecha")
            self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=16)
            
            self.tree.heading("grupo", text="ID VENTA")
            self.tree.heading("items", text="ITEMS")
            self.tree.heading("total", text="TOTAL ($)")
            self.tree.heading("fecha", text="FECHA Y HORA")
            
            self.tree.column("grupo", width=150, anchor="center")
            self.tree.column("items", width=100, anchor="center")
            self.tree.column("total", width=120, anchor="center")
            self.tree.column("fecha", width=180, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars (más visibles)
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Scrollbar horizontal para columnas anchas
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, columnspan=2, sticky='ew')
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind para mostrar detalles
        self.tree.bind('<Double-1>', self.mostrar_detalles_venta)
        
        # ============================================
        # 7. BOTONES DE ACCIÓN 
        # ============================================
        botones_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="transparent")
        botones_frame.pack(fill='x', pady=(0, 10))
        
        btn_actualizar = ctk.CTkButton(botones_frame,
                                      text="🔄 ACTUALIZAR LISTA",
                                      command=self.cargar_ventas,
                                      fg_color="#45b7d1",
                                      hover_color="#3aa1c9",
                                      height=45,  
                                      width=180,  
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      corner_radius=8)
        btn_actualizar.pack(side='left', padx=10)
        
        btn_detalles = ctk.CTkButton(botones_frame,
                                    text="📋 VER DETALLES DE VENTA",
                                    command=self.mostrar_detalles_seleccionados,
                                    fg_color="#4ecdc4",
                                    hover_color="#3ebbb4",
                                    height=45,
                                    width=200,
                                    font=ctk.CTkFont(size=13, weight="bold"),
                                    corner_radius=8)
        btn_detalles.pack(side='left', padx=10)
        
        btn_volver = ctk.CTkButton(botones_frame,
                                  text="↶ VOLVER AL PUNTO DE VENTA",
                                  command=self.cerrar_y_volver,
                                  fg_color="#ff6b6b",
                                  hover_color="#ff5a5a",
                                  height=45,
                                  width=220,
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  corner_radius=8)
        btn_volver.pack(side='right', padx=10)
    
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
            self.panel_menu.place(x=-280, y=100)
            self.menu_abierto = False
    
    def focus_filtro_usuario(self):
        """Coloca el foco en el campo de filtro de usuario"""
        if self.tipo_usuario == 'jefe' and hasattr(self, 'filtro_usuario'):
            self.filtro_usuario.focus_set()
        self.toggle_menu()
    
    # ============================================
    # NUEVAS FUNCIONALIDADES AGREGADAS
    # ============================================
    def mostrar_ventas_dia(self):
        """Muestra las ventas del día actual"""
        fecha_actual = datetime.now().date()
        fecha_inicio = datetime.combine(fecha_actual, datetime.min.time())
        fecha_fin = datetime.combine(fecha_actual, datetime.max.time())
        
        try:
            ventas = obtener_ventas_por_rango_fechas(fecha_inicio, fecha_fin)
            
            # Mostrar resultados
            self.mostrar_resultados_temporales(
                f"📊 VENTAS DEL DÍA: {fecha_actual.strftime('%d/%m/%Y')}",
                ventas
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas del día: {str(e)}")
        
        self.toggle_menu()
    
    def mostrar_ventas_semana(self):
        """Muestra las ventas de la semana actual"""
        fecha_actual = datetime.now().date()
        # Obtener inicio de semana (lunes)
        fecha_inicio_semana = fecha_actual - timedelta(days=fecha_actual.weekday())
        fecha_fin_semana = fecha_inicio_semana + timedelta(days=6)
        
        fecha_inicio = datetime.combine(fecha_inicio_semana, datetime.min.time())
        fecha_fin = datetime.combine(fecha_fin_semana, datetime.max.time())
        
        try:
            ventas = obtener_ventas_por_rango_fechas(fecha_inicio, fecha_fin)
            
            # Mostrar resultados
            self.mostrar_resultados_temporales(
                f"📅 VENTAS DE LA SEMANA: {fecha_inicio_semana.strftime('%d/%m/%Y')} - {fecha_fin_semana.strftime('%d/%m/%Y')}",
                ventas
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas de la semana: {str(e)}")
        
        self.toggle_menu()
    
    def mostrar_ventas_mes(self):
        """Muestra las ventas del mes actual"""
        fecha_actual = datetime.now().date()
        primer_dia_mes = fecha_actual.replace(day=1)
        
        # Obtener último día del mes
        ultimo_dia_mes = primer_dia_mes + relativedelta(months=1, days=-1)
        
        fecha_inicio = datetime.combine(primer_dia_mes, datetime.min.time())
        fecha_fin = datetime.combine(ultimo_dia_mes, datetime.max.time())
        
        try:
            ventas = obtener_ventas_por_rango_fechas(fecha_inicio, fecha_fin)
            
            # Mostrar resultados
            nombre_mes = fecha_actual.strftime('%B').upper()
            self.mostrar_resultados_temporales(
                f"🗓️ VENTAS DEL MES DE {nombre_mes} {fecha_actual.year}",
                ventas
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas del mes: {str(e)}")
        
        self.toggle_menu()
    
    def mostrar_apartado_dia(self):
        """Muestra ventana para apartarse por día específico"""
        # Crear ventana para seleccionar fecha
        fecha_window = ctk.CTkToplevel(self.root)
        fecha_window.title("📅 Seleccionar Fecha")
        fecha_window.geometry("400x300")
        
        # Centrar ventana
        fecha_window.update_idletasks()
        x = (fecha_window.winfo_screenwidth() // 2) - (200)
        y = (fecha_window.winfo_screenheight() // 2) - (150)
        fecha_window.geometry(f"400x300+{x}+{y}")
        
        # Mantener referencia
        fecha_window.transient(self.root)
        fecha_window.grab_set()
        self.ventanas_secundarias.append(fecha_window)
        
        def on_close():
            if fecha_window in self.ventanas_secundarias:
                self.ventanas_secundarias.remove(fecha_window)
            fecha_window.destroy()
        
        fecha_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Frame principal
        main_frame = ctk.CTkFrame(fecha_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, 
                     text="📅 SELECCIONAR FECHA", 
                     font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
                     text_color="#2c3e50").pack(pady=20)
        
        # Frame para fecha
        fecha_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        fecha_frame.pack(pady=20)
        
        # Año
        ctk.CTkLabel(fecha_frame, text="Año:", 
                    font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        year_var = tk.StringVar(value=str(datetime.now().year))
        year_spinbox = ctk.CTkEntry(fecha_frame, 
                                   textvariable=year_var,
                                   width=80,
                                   font=ctk.CTkFont(size=13))
        year_spinbox.grid(row=0, column=1, padx=5, pady=5)
        
        # Mes
        ctk.CTkLabel(fecha_frame, text="Mes:", 
                    font=ctk.CTkFont(size=13)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        month_combo = ctk.CTkComboBox(fecha_frame,
                                     values=meses,
                                     font=ctk.CTkFont(size=13),
                                     width=150)
        month_combo.set(meses[datetime.now().month - 1])
        month_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Día
        ctk.CTkLabel(fecha_frame, text="Día:", 
                    font=ctk.CTkFont(size=13)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        day_var = tk.StringVar(value=str(datetime.now().day))
        day_spinbox = ctk.CTkEntry(fecha_frame, 
                                  textvariable=day_var,
                                  width=80,
                                  font=ctk.CTkFont(size=13))
        day_spinbox.grid(row=2, column=1, padx=5, pady=5)
        
        # Función para procesar la fecha seleccionada
        def procesar_fecha():
            try:
                año = int(year_var.get())
                mes = meses.index(month_combo.get()) + 1
                día = int(day_var.get())
                
                fecha_seleccionada = datetime(año, mes, día).date()
                fecha_inicio = datetime.combine(fecha_seleccionada, datetime.min.time())
                fecha_fin = datetime.combine(fecha_seleccionada, datetime.max.time())
                
                ventas = obtener_ventas_por_rango_fechas(fecha_inicio, fecha_fin)
                
                fecha_window.destroy()
                if fecha_window in self.ventanas_secundarias:
                    self.ventanas_secundarias.remove(fecha_window)
                
                # Mostrar resultados
                self.mostrar_resultados_temporales(
                    f"👥 VENTAS DEL DÍA: {fecha_seleccionada.strftime('%d/%m/%Y')}",
                    ventas
                )
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese una fecha válida")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar las ventas: {str(e)}")
        
        # Botones
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(pady=20)
        
        btn_aceptar = ctk.CTkButton(botones_frame,
                                  text="✅ ACEPTAR",
                                  command=procesar_fecha,
                                  fg_color="#2ecc71",
                                  hover_color="#27ae60",
                                  width=120,
                                  height=35,
                                  font=ctk.CTkFont(size=13))
        btn_aceptar.pack(side='left', padx=10)
        
        btn_cancelar = ctk.CTkButton(botones_frame,
                                   text="❌ CANCELAR",
                                   command=on_close,
                                   fg_color="#e74c3c",
                                   hover_color="#c0392b",
                                   width=120,
                                   height=35,
                                   font=ctk.CTkFont(size=13))
        btn_cancelar.pack(side='left', padx=10)
        
        self.toggle_menu()
    
    def mostrar_resultados_temporales(self, titulo, ventas):
        """Muestra los resultados de ventas por período temporal"""
        if not ventas:
            messagebox.showinfo("Sin Resultados", f"No hay ventas registradas para este período.")
            return
        
        # Calcular estadísticas
        total_ventas = len(ventas)
        monto_total = sum(venta[4] for venta in ventas)
        total_productos = sum(venta[3] for venta in ventas)
        
        # Crear ventana de resultados
        resultados_window = ctk.CTkToplevel(self.root)
        resultados_window.title(titulo)
        resultados_window.geometry("1000x700")
        
        # Centrar ventana
        resultados_window.update_idletasks()
        x = (resultados_window.winfo_screenwidth() // 2) - (500)
        y = (resultados_window.winfo_screenheight() // 2) - (350)
        resultados_window.geometry(f"1000x700+{x}+{y}")
        
        # Mantener referencia
        resultados_window.transient(self.root)
        resultados_window.grab_set()
        self.ventanas_secundarias.append(resultados_window)
        
        def on_close():
            if resultados_window in self.ventanas_secundarias:
                self.ventanas_secundarias.remove(resultados_window)
            resultados_window.destroy()
        
        resultados_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Frame principal
        main_frame = ctk.CTkFrame(resultados_window)
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Título
        ctk.CTkLabel(main_frame, 
                     text=titulo, 
                     font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                     text_color="#2c3e50").pack(pady=(0, 20))
        
        # Estadísticas
        stats_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#ecf0f1")
        stats_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(padx=20, pady=15)
        
        ctk.CTkLabel(stats_container, 
                     text=f"📊 Total de ventas: {total_ventas}", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#2c3e50").pack(side='left', padx=20)
        
        ctk.CTkLabel(stats_container, 
                     text=f"💰 Monto total: ${monto_total:.2f}", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#27ae60").pack(side='left', padx=20)
        
        ctk.CTkLabel(stats_container, 
                     text=f"🛒 Productos vendidos: {total_productos}", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#e74c3c").pack(side='left', padx=20)
        
        # Tabla de ventas
        tree_frame = ctk.CTkFrame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=(0, 20))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Configurar Treeview
        columns = ("grupo", "usuario", "items", "total", "fecha")
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        tree.heading("grupo", text="ID VENTA")
        tree.heading("usuario", text="USUARIO")
        tree.heading("items", text="ITEMS")
        tree.heading("total", text="TOTAL ($)")
        tree.heading("fecha", text="FECHA Y HORA")
        
        tree.column("grupo", width=150, anchor="center")
        tree.column("usuario", width=150, anchor="center")
        tree.column("items", width=100, anchor="center")
        tree.column("total", width=120, anchor="center")
        tree.column("fecha", width=180, anchor="center")
        
        tree.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        h_scrollbar.grid(row=1, column=0, columnspan=2, sticky='ew')
        tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Insertar ventas
        for venta in ventas:
            tree.insert("", tk.END, values=(
                venta[0],  # venta_id_gruppo
                venta[2] or "N/A",  # username
                venta[3],  # total_items
                f"${venta[4]:.2f}",  # total_venta
                venta[5].strftime("%Y-%m-%d %H:%M:%S")  # fecha
            ))
        
        # Botón cerrar
        btn_cerrar = ctk.CTkButton(main_frame,
                                  text="CERRAR",
                                  command=on_close,
                                  fg_color="#3498db",
                                  hover_color="#2980b9",
                                  height=40,
                                  width=150,
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  corner_radius=8)
        btn_cerrar.pack()
    
    def mostrar_estadisticas_detalladas(self):
        """Muestra estadísticas detalladas en una ventana emergente"""
        estadisticas = obtener_estadisticas_ventas() if self.tipo_usuario == 'jefe' else obtener_estadisticas_usuario(self.id_usuario)
        
        # Crear ventana de estadísticas
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title("📊 Estadísticas Detalladas")
        stats_window.geometry("600x500")
        
        # Centrar ventana
        stats_window.update_idletasks()
        ancho = stats_window.winfo_width()
        alto = stats_window.winfo_height()
        x = (stats_window.winfo_screenwidth() // 2) - (ancho // 2)
        y = (stats_window.winfo_screenheight() // 2) - (alto // 2)
        stats_window.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # Mantener referencia
        stats_window.transient(self.root)
        stats_window.grab_set()
        self.ventanas_secundarias.append(stats_window)
        
        def on_close():
            if stats_window in self.ventanas_secundarias:
                self.ventanas_secundarias.remove(stats_window)
            stats_window.destroy()
        
        stats_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Frame principal
        main_frame = ctk.CTkFrame(stats_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(main_frame,
                     text="📊 ESTADÍSTICAS DETALLADAS DE VENTAS",
                     font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                     text_color="#2c3e50").pack(pady=20)
        
        # Frame para estadísticas
        stats_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#ecf0f1")
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear etiquetas de estadísticas
        stats_data = [
            (f"📊 Total de ventas:", f"{estadisticas.get('total_ventas', 0)}", "#3498db"),
            (f"💰 Monto total:", f"${estadisticas.get('monto_total', 0):.2f}", "#2ecc71"),
            (f"🛒 Productos vendidos:", f"{estadisticas.get('total_productos', 0)}", "#f39c12")
        ]
        
        if self.tipo_usuario == 'jefe' and estadisticas.get('total_ventas', 0) > 0:
            venta_promedio = estadisticas.get('monto_total', 0) / estadisticas.get('total_ventas', 1)
            stats_data.append((f"📈 Venta promedio:", f"${venta_promedio:.2f}", "#9b59b6"))
        
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
                                  command=on_close,
                                  fg_color="#95a5a6",
                                  hover_color="#7f8c8d",
                                  height=40,
                                  width=150,
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  corner_radius=8)
        btn_cerrar.pack(pady=20)
        
        self.toggle_menu()
    
    # ============================================
    # MÉTODOS DE GESTIÓN DE HISTORIAL
    # ============================================
    def cargar_ventas(self):
        """Carga las ventas según el tipo de usuario"""
        try:
            if self.tipo_usuario == 'jefe':
                ventas = obtener_ventas_agrupadas()
                estadisticas = obtener_estadisticas_ventas()
            else:
                ventas = obtener_ventas_agrupadas_por_usuario(self.id_usuario)
                estadisticas = obtener_estadisticas_usuario(self.id_usuario)
            
            self.mostrar_ventas(ventas)
            self.actualizar_estadisticas(estadisticas)
            self.ventas_actuales = ventas
            self.estadisticas_actuales = estadisticas
            
            # Cerrar menú si está abierto
            if self.menu_abierto:
                self.toggle_menu()
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas: {str(e)}")
    
    def aplicar_filtro(self):
        """Aplica filtro por usuario (solo para jefes)"""
        if self.tipo_usuario != 'jefe':
            return
            
        usuario_filtro = self.filtro_usuario.get().strip()
        if not usuario_filtro:
            messagebox.showwarning("Advertencia", "Ingrese un nombre de usuario para filtrar.")
            return
        
        ventas = obtener_ventas_agrupadas()
        ventas_filtradas = [v for v in ventas if usuario_filtro.lower() in str(v[2]).lower()]
        
        self.mostrar_ventas(ventas_filtradas)
        
        # Calcular estadísticas filtradas
        total_ventas = len(ventas_filtradas)
        monto_total = sum(v[4] for v in ventas_filtradas)
        total_productos = sum(v[3] for v in ventas_filtradas)
        
        estadisticas_filtradas = {
            'total_ventas': total_ventas,
            'monto_total': monto_total,
            'total_productos': total_productos
        }
        
        self.actualizar_estadisticas(estadisticas_filtradas)
        
        messagebox.showinfo("Filtro Aplicado", 
                           f"Se encontraron {total_ventas} ventas para el usuario '{usuario_filtro}'.")
    
    def mostrar_ventas(self, ventas):
        """Muestra las ventas en la tabla"""
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Insertar ventas
        for venta in ventas:
            if self.tipo_usuario == 'jefe':
                self.tree.insert("", tk.END, values=(
                    venta[0],  # venta_id_gruppo
                    venta[2] or "N/A",  # username
                    venta[3],  # total_items
                    f"${venta[4]:.2f}",  # total_venta
                    venta[5].strftime("%Y-%m-%d %H:%M:%S")  # fecha
                ))
            else:
                self.tree.insert("", tk.END, values=(
                    venta[0],  # venta_id_gruppo
                    venta[3],  # total_items
                    f"${venta[4]:.2f}",  # total_venta
                    venta[5].strftime("%Y-%m-%d %H:%M:%S")  # fecha
                ))
    
    def mostrar_detalles_venta(self, event=None):
        """Muestra los detalles de la venta al hacer doble clic"""
        self.mostrar_detalles_seleccionados()
    
    def mostrar_detalles_seleccionados(self):
        """Muestra los detalles de la venta seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una venta para ver los detalles.")
            return
        
        item = self.tree.item(seleccion[0])
        venta_id_gruppo = item['values'][0]
        
        detalles = obtener_detalles_venta(venta_id_gruppo)
        self.mostrar_detalles_completos(detalles, venta_id_gruppo)
    
    def mostrar_detalles_completos(self, detalles, venta_id_gruppo):
        """Muestra los detalles completos de una venta"""
        if not detalles:
            messagebox.showinfo("Detalles", "No se encontraron detalles para esta venta.")
            return
        
        # Crear ventana de detalles 
        detalle_window = ctk.CTkToplevel(self.root)
        detalle_window.title(f"📋 Detalles de Venta - {venta_id_gruppo}")
        detalle_window.geometry("900x550")
        
        # Centrar ventana
        detalle_window.update_idletasks()
        ancho = 900
        alto = 550
        x = (detalle_window.winfo_screenwidth() // 2) - (ancho // 2)
        y = (detalle_window.winfo_screenheight() // 2) - (alto // 2)
        detalle_window.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # Mantener referencia
        detalle_window.transient(self.root)
        detalle_window.grab_set()
        self.ventanas_secundarias.append(detalle_window)
        
        def on_close():
            if detalle_window in self.ventanas_secundarias:
                self.ventanas_secundarias.remove(detalle_window)
            detalle_window.destroy()
        
        detalle_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Frame principal
        main_frame = ctk.CTkFrame(detalle_window)
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(main_frame, 
                     text=f"📋 DETALLES DE VENTA: {venta_id_gruppo}", 
                     font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                     text_color="#2c3e50").pack(pady=(0, 25))
        
        # Frame para treeview de detalles
        tree_frame = ctk.CTkFrame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=10)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Configurar estilo del Treeview de detalles
        style_detalles = ttk.Style()
        style_detalles.theme_use("default")
        style_detalles.configure("Treeview.Heading", 
                                font=('Arial', 11, 'bold'), 
                                background='#34495e', 
                                foreground='white',
                                padding=8)
        style_detalles.configure("Treeview", 
                                font=('Arial', 10), 
                                rowheight=32,  
                                background='white',
                                fieldbackground='white',
                                foreground='black')
        
        # Crear Treeview para detalles 
        columns = ("tipo", "producto", "cantidad", "precio", "subtotal")
        tree_detalles = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        tree_detalles.heading("tipo", text="TIPO")
        tree_detalles.heading("producto", text="PRODUCTO/SERVICIO")
        tree_detalles.heading("cantidad", text="CANTIDAD")
        tree_detalles.heading("precio", text="PRECIO UNITARIO ($)")
        tree_detalles.heading("subtotal", text="SUBTOTAL ($)")
        
        tree_detalles.column("tipo", width=120, anchor="center")  
        tree_detalles.column("producto", width=250, anchor="w")  
        tree_detalles.column("cantidad", width=100, anchor="center")  
        tree_detalles.column("precio", width=150, anchor="center")  
        tree_detalles.column("subtotal", width=150, anchor="center")  
        
        # Scrollbar para detalles
        scrollbar_detalles = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_detalles.yview)
        scrollbar_detalles.grid(row=0, column=1, sticky='ns')
        tree_detalles.configure(yscrollcommand=scrollbar_detalles.set)
        
        tree_detalles.grid(row=0, column=0, sticky='nsew')
        
        # Insertar detalles
        total_venta = 0
        for detalle in detalles:
            # Determinar si es producto o servicio
            if detalle[3]:  # Si tiene id_producto, es producto
                tipo = "📦 Producto"
                nombre = detalle[4] or f"Producto ID: {detalle[3]}"
            else:  # Si no tiene id_producto pero tiene nombre_service, es servicio
                tipo = "🛠️ Servicio"
                nombre = detalle[4] or "Servicio"
            
            cantidad = detalle[5]
            precio = detalle[6]
            subtotal = detalle[7]
            total_venta += subtotal
            
            tree_detalles.insert("", tk.END, values=(
                tipo,
                nombre,
                cantidad,
                f"${precio:.2f}",
                f"${subtotal:.2f}"
            ))
        
        # Frame para total (más grande)
        total_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        total_frame.pack(fill='x', pady=15)
        
        ctk.CTkLabel(total_frame, 
                     text="💰 TOTAL DE LA VENTA:", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#2c3e50").pack(side='left')
        
        ctk.CTkLabel(total_frame, 
                     text=f"${total_venta:.2f}", 
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#27ae60").pack(side='left', padx=15)
        
        # Botón cerrar (más grande)
        btn_cerrar = ctk.CTkButton(main_frame,
                                  text="CERRAR",
                                  command=on_close,
                                  fg_color="#ff6b6b",
                                  hover_color="#ff5a5a",
                                  height=40,
                                  width=150,
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  corner_radius=8)
        btn_cerrar.pack(pady=15)
    
    def actualizar_estadisticas(self, estadisticas):
        """Actualiza las estadísticas de ventas"""
        self.label_total_ventas.configure(text=f"📊 Total de ventas: {estadisticas.get('total_ventas', 0)}")
        self.label_monto_total.configure(text=f"💰 Monto total: ${estadisticas.get('monto_total', 0):.2f}")
        self.label_total_productos.configure(text=f"🛒 Productos vendidos: {estadisticas.get('total_productos', 0)}")
    
    def exportar_reporte(self):
        """Exporta un reporte de ventas a PDF (solo para jefes)"""
        if self.tipo_usuario != 'jefe':
            messagebox.showwarning("Acceso Restringido", "Solo los jefes pueden exportar reportes.")
            return
        
        if not hasattr(self, 'ventas_actuales') or not self.ventas_actuales:
            messagebox.showwarning("Sin Datos", "No hay ventas para exportar.")
            return
        
        # Solicitar ubicación para guardar el archivo
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reporte_ventas_{fecha_actual}.pdf"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=nombre_archivo,
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        
        if not file_path:
            return  # Usuario canceló
        
        try:
            # Crear el PDF
            c = canvas.Canvas(file_path, pagesize=A4)
            ancho, alto = A4
            
            # Título
            c.setFont("Helvetica-Bold", 18)  
            c.drawString(50, alto - 50, "💈 Barbería Bravo - Reporte de Ventas")
            
            # Información del reporte
            c.setFont("Helvetica", 11)  
            fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            c.drawString(50, alto - 80, f"Fecha de generación: {fecha_generacion}")
            c.drawString(50, alto - 100, f"Generado por: {self.username}")
            
            # Estadísticas
            c.setFont("Helvetica-Bold", 14)  
            c.drawString(50, alto - 130, "📊 ESTADÍSTICAS GENERALES")
            c.setFont("Helvetica", 11)  
            c.drawString(50, alto - 155, f"• Total de ventas: {self.estadisticas_actuales.get('total_ventas', 0)}")
            c.drawString(50, alto - 175, f"• Monto total: ${self.estadisticas_actuales.get('monto_total', 0):.2f}")
            c.drawString(50, alto - 195, f"• Productos vendidos: {self.estadisticas_actuales.get('total_productos', 0)}")
            
            # Tabla de ventas
            y_pos = alto - 230
            c.setFont("Helvetica-Bold", 14) 
            c.drawString(50, y_pos, "📋 VENTAS REGISTRADAS")
            
            # Encabezados de la tabla
            y_pos -= 25
            c.setFont("Helvetica-Bold", 11)  
            c.drawString(50, y_pos, "ID Venta")
            c.drawString(140, y_pos, "Usuario")
            c.drawString(230, y_pos, "Items")
            c.drawString(290, y_pos, "Total")
            c.drawString(360, y_pos, "Fecha y Hora")
            
            # Línea separadora
            y_pos -= 5
            c.line(50, y_pos, 550, y_pos)
            
            # Datos de ventas
            c.setFont("Helvetica", 10)  # Fuente más grande
            y_pos -= 20
            
            for venta in self.ventas_actuales:
                if y_pos < 100:  # Nueva página si se llega al final
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_pos = alto - 50
                
                c.drawString(50, y_pos, str(venta[0]))  # ID Venta
                c.drawString(140, y_pos, str(venta[2] or "N/A"))  # Usuario
                c.drawString(230, y_pos, str(venta[3]))  # Items
                c.drawString(290, y_pos, f"${venta[4]:.2f}")  # Total
                c.drawString(360, y_pos, venta[5].strftime("%Y-%m-%d %H:%M:%S"))  # Fecha
                y_pos -= 18
            
            # Pie de página
            c.setFont("Helvetica-Oblique", 9)  # Fuente más grande
            c.drawString(50, 40, f"Reporte generado automáticamente por el Sistema de Barbería Bravo")
            c.drawString(50, 25, "Confidencial - Uso interno")
            
            # Guardar el PDF
            c.save()
            
            messagebox.showinfo("Exportación Exitosa", 
                              f"✅ Reporte exportado correctamente a:\n{file_path}")
            
            # Preguntar si desea abrir el archivo
            if messagebox.askyesno("Abrir Reporte", "¿Desea abrir el reporte generado?"):
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # Linux/Mac
                    os.system(f'open "{file_path}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{file_path}"')
        
        except Exception as e:
            messagebox.showerror("Error", f"❌ No se pudo exportar el reporte:\n{str(e)}")
    
    def cerrar_todas_ventanas_secundarias(self):
        """Cierra todas las ventanas secundarias"""
        for ventana in self.ventanas_secundarias[:]:  # Copia de la lista
            try:
                ventana.destroy()
            except:
                pass
        self.ventanas_secundarias.clear()
    
    def cerrar_y_volver(self):
        """Cierra HistorialView y vuelve a UserApp2"""
        # Cerrar todas las ventanas secundarias primero
        self.cerrar_todas_ventanas_secundarias()
        
        if self.parent:
            self.root.destroy()
            self.parent.root.deiconify()  # Muestra nuevamente UserApp2
        else:
            self.root.destroy()
    
    def __del__(self):
        """Destructor - asegura que UserApp2 se muestre al cerrar"""
        self.cerrar_todas_ventanas_secundarias()
        if self.parent:
            self.parent.root.deiconify()

if __name__ == "__main__":
    # Para pruebas
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.withdraw()
    app = HistorialView("admin", "jefe", 1)
    root.mainloop()