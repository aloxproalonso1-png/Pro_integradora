import tkinter as tk
from tkinter import messagebox, ttk
from poductos_controller import ver_producto, agregar_productos, actualizar_productos, eliminar_producto


class UserApp2:
    def __init__(self, username):
        self.username = username
        self.carrito = []  # Lista para almacenar los productos en el carrito
        self.root = tk.Tk()
        self.root.title(f"Punto de Venta - {username}")
        self.root.geometry("900x650")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(True, True)        
        
        self.crear_elementos()
        self.ver_productos()
        self.root.mainloop()

    def crear_elementos(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Encabezado
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text=f"Punto de Venta - {self.username}", font=("Arial", 22, "bold"), 
                bg='#f0f0f0').pack(side='left')
        tk.Button(header_frame, text="Cerrar sesión", width=15, command=self.cerrar_sesion,
                 bg='#ff6b6b', fg='white', font=('Arial', 10, 'bold')).pack(side='right')
        
        # Frame de botones principales
        frame_botones = tk.Frame(main_frame, bg='#f0f0f0')
        frame_botones.pack(fill='x', pady=10)
        
        botones = [
            ("Gestión de Productos", self.gestionar_productos),
            ("Ver usuarios", self.abrir_user_view)
        ]
        
        for texto, comando in botones:
            btn = tk.Button(frame_botones, text=texto, width=20, command=comando,
                           bg='#4ecdc4', fg='white', font=('Arial', 10, 'bold'),
                           relief='raised', bd=2)
            btn.pack(side='left', padx=5, pady=5)
        
        # Sección de productos (similar a la imagen)
        productos_frame = tk.LabelFrame(main_frame, text="Punto de Venta", 
                                       font=("Arial", 14, "bold"), bg='#f0f0f0')
        productos_frame.pack(fill='both', expand=True, pady=10)
        
        # Campos de entrada (similares a la imagen)
        form_frame = tk.Frame(productos_frame, bg='#f0f0f0')
        form_frame.pack(fill='x', pady=10)
        
        # Fila 1 - Selección de producto
        tk.Label(form_frame, text="Producto", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        # Combobox para seleccionar producto
        self.combo_productos = ttk.Combobox(form_frame, width=20, font=('Arial', 10), state="readonly")
        self.combo_productos.grid(row=0, column=1, padx=5, pady=5)
        self.combo_productos.bind('<<ComboboxSelected>>', self.actualizar_precio)
        
        tk.Label(form_frame, text="Cantidad", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.entry_cantidad = tk.Entry(form_frame, width=10, font=('Arial', 10))
        self.entry_cantidad.grid(row=0, column=3, padx=5, pady=5)
        self.entry_cantidad.insert(0, "1")  # Cantidad por defecto
        
        tk.Label(form_frame, text="Precio Unitario", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.label_precio = tk.Label(form_frame, text="$0.00", bg='#f0f0f0', font=('Arial', 10, 'bold'), fg='#2e86ab')
        self.label_precio.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        
        # Botones de acción (similares a la imagen)
        btn_agregar = tk.Button(form_frame, text="Agregar", width=10, command=self.agregar_al_carrito,
                               bg='#45b7d1', fg='white', font=('Arial', 10, 'bold'))
        btn_agregar.grid(row=0, column=6, padx=10, pady=5)
        
        # Fila 2 - Botones inferiores
        action_frame = tk.Frame(form_frame, bg='#f0f0f0')
        action_frame.grid(row=1, column=0, columnspan=7, pady=10)
        
        btn_cancelar = tk.Button(action_frame, text="Cancelar Venta", width=12, command=self.limpiar_carrito,
                                bg='#ff6b6b', fg='white', font=('Arial', 10, 'bold'))
        btn_cancelar.pack(side='left', padx=10)
        
        btn_pagar = tk.Button(action_frame, text="Pagar", width=12, command=self.procesar_pago,
                             bg='#96ceb4', fg='white', font=('Arial', 10, 'bold'))
        btn_pagar.pack(side='left', padx=10)
        
        # Total
        total_frame = tk.Frame(action_frame, bg='#f0f0f0')
        total_frame.pack(side='left', padx=20)
        
        tk.Label(total_frame, text="Total:", bg='#f0f0f0', font=('Arial', 12, 'bold')).pack(side='left')
        self.label_total = tk.Label(total_frame, text="$0.00", bg='#f0f0f0', font=('Arial', 12, 'bold'), fg='#2e86ab')
        self.label_total.pack(side='left', padx=5)
        
        # Lista de productos en el carrito (tabla)
        tk.Label(productos_frame, text="Productos en el Carrito", font=("Arial", 12, "bold"), 
                bg='#f0f0f0').pack(pady=(10, 5))
        
        # Crear tabla para el carrito
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#4ecdc4')
        style.configure("Treeview", font=('Arial', 9), rowheight=25)
        
        self.tree_carrito = ttk.Treeview(productos_frame, 
                                columns=("producto", "cantidad", "precio_unitario", "subtotal"), 
                                show="headings", height=8)
        
        # Encabezados del carrito
        self.tree_carrito.heading("producto", text="Producto")
        self.tree_carrito.heading("cantidad", text="Cantidad")
        self.tree_carrito.heading("precio_unitario", text="Precio Unitario")
        self.tree_carrito.heading("subtotal", text="Subtotal")

        # Columnas del carrito
        self.tree_carrito.column("producto", width=200, anchor="center")
        self.tree_carrito.column("cantidad", width=100, anchor="center")
        self.tree_carrito.column("precio_unitario", width=120, anchor="center")
        self.tree_carrito.column("subtotal", width=120, anchor="center")
        
        # Scrollbar para la tabla del carrito
        scrollbar = ttk.Scrollbar(productos_frame, orient="vertical", command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scrollbar.set)
        self.tree_carrito.pack(side='left', fill='both', expand=True, padx=(0, 5))
        scrollbar.pack(side='right', fill='y')

    def actualizar_precio(self, event=None):
        """Actualiza el precio cuando se selecciona un producto"""
        producto_seleccionado = self.combo_productos.get()
        if producto_seleccionado:
            # Buscar el precio del producto seleccionado
            for producto in self.productos_disponibles:
                # El formato es: "Nombre - $Precio"
                nombre_completo = f"{producto[1]} - ${producto[3]}"
                if nombre_completo == producto_seleccionado:
                    precio = float(producto[3])  # Asegurar que es float
                    self.label_precio.config(text=f"${precio:.2f}")
                    break

    def agregar_al_carrito(self):
        """Agrega el producto seleccionado al carrito"""
        producto_seleccionado = self.combo_productos.get()
        cantidad_text = self.entry_cantidad.get().strip()
        
        if not producto_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un producto.")
            return
        
        if not cantidad_text or not cantidad_text.isdigit():
            messagebox.showwarning("Advertencia", "Ingrese una cantidad válida.")
            return
        
        cantidad = int(cantidad_text)
        if cantidad <= 0:
            messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0.")
            return
        
        # Buscar el producto seleccionado
        for producto in self.productos_disponibles:
            nombre_completo = f"{producto[1]} - ${producto[3]}"
            if nombre_completo == producto_seleccionado:
                precio_unitario = float(producto[3])  # Convertir a float
                subtotal = precio_unitario * cantidad
                
                # Verificar si el producto ya está en el carrito
                producto_existente = None
                for item in self.carrito:
                    if item['id'] == producto[0]:
                        producto_existente = item
                        break
                
                if producto_existente:
                    # Actualizar cantidad y subtotal
                    producto_existente['cantidad'] += cantidad
                    producto_existente['subtotal'] = producto_existente['cantidad'] * precio_unitario
                else:
                    # Agregar nuevo producto al carrito
                    self.carrito.append({
                        'id': producto[0],
                        'nombre': producto[1],
                        'cantidad': cantidad,
                        'precio_unitario': precio_unitario,
                        'subtotal': subtotal
                    })
                
                # Actualizar la tabla del carrito
                self.actualizar_carrito()
                self.calcular_total()
                
                # Limpiar selección
                self.combo_productos.set('')
                self.label_precio.config(text="$0.00")
                self.entry_cantidad.delete(0, tk.END)
                self.entry_cantidad.insert(0, "1")
                break

    def actualizar_carrito(self):
        """Actualiza la tabla del carrito"""
        # Limpiar tabla
        for row in self.tree_carrito.get_children():
            self.tree_carrito.delete(row)
        
        # Insertar productos del carrito
        for item in self.carrito:
            self.tree_carrito.insert("", tk.END, values=(
                item['nombre'],
                item['cantidad'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            ))

    def calcular_total(self):
        """Calcula el total de la venta"""
        total = sum(item['subtotal'] for item in self.carrito)
        self.label_total.config(text=f"${total:.2f}")

    def limpiar_carrito(self):
        """Limpia el carrito y reinicia la interfaz"""
        self.carrito = []
        self.actualizar_carrito()
        self.calcular_total()
        self.combo_productos.set('')
        self.label_precio.config(text="$0.00")
        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, "1")

    def procesar_pago(self):
        """Procesa el pago de la venta"""
        if not self.carrito:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito.")
            return
        
        total = sum(item['subtotal'] for item in self.carrito)
        
        # Mostrar resumen de la venta
        resumen = "Resumen de la venta:\n\n"
        for item in self.carrito:
            resumen += f"{item['nombre']} x {item['cantidad']} = ${item['subtotal']:.2f}\n"
        resumen += f"\nTotal: ${total:.2f}"
        
        confirmar = messagebox.askyesno("Confirmar Pago", resumen)
        
        if confirmar:
            # Aquí iría la lógica para guardar la venta en la base de datos
            messagebox.showinfo("Éxito", f"Venta procesada exitosamente!\nTotal: ${total:.2f}")
            self.limpiar_carrito()

    def ver_productos(self):
        """Carga los productos disponibles en el combobox"""
        try:
            # Obtener productos
            self.productos_disponibles = ver_producto()
            print(f"DEBUG: Productos obtenidos: {self.productos_disponibles}")
            
            if not self.productos_disponibles:
                messagebox.showwarning("Advertencia", "No hay productos disponibles en el inventario.")
                return
            
            # Actualizar combobox
            productos_formato = []
            for producto in self.productos_disponibles:
                # producto[1] = nombre, producto[3] = precio
                if len(producto) >= 4:  # Asegurar que tiene al menos 4 elementos
                    nombre = producto[1] if producto[1] else "Sin nombre"
                    precio = producto[3] if producto[3] else 0
                    productos_formato.append(f"{nombre} - ${precio}")
            
            self.combo_productos['values'] = productos_formato
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {str(e)}")

    def gestionar_productos(self):
        """Abre la ventana para gestionar productos (agregar/editar/eliminar)"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Gestión de Productos")
        ventana.geometry("600x500")
        ventana.configure(bg='#f0f0f0')
        ventana.transient(self.root)
        ventana.grab_set()
        
        # Crear pestañas
        notebook = ttk.Notebook(ventana)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña de agregar producto
        frame_agregar = ttk.Frame(notebook)
        notebook.add(frame_agregar, text="Agregar Producto")
        
        self.crear_formulario_agregar(frame_agregar, ventana)
        
        # Pestaña de lista de productos
        frame_lista = ttk.Frame(notebook)
        notebook.add(frame_lista, text="Inventario")
        
        self.crear_tabla_inventario(frame_lista, ventana)

    def crear_formulario_agregar(self, parent, ventana):
        """Crea el formulario para agregar productos"""
        tk.Label(parent, text="Nombre del producto", bg='#f0f0f0').pack(pady=5)
        entry_nombre = tk.Entry(parent, width=30)
        entry_nombre.pack(pady=5)
        
        tk.Label(parent, text="Stock", bg='#f0f0f0').pack(pady=5)
        entry_stock = tk.Entry(parent, width=30)
        entry_stock.pack(pady=5)
        
        tk.Label(parent, text="Precio", bg='#f0f0f0').pack(pady=5)
        entry_precio = tk.Entry(parent, width=30)
        entry_precio.pack(pady=5)
        
        tk.Label(parent, text="Proveedor", bg='#f0f0f0').pack(pady=5)
        entry_proveedor = tk.Entry(parent, width=30)
        entry_proveedor.pack(pady=5)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            stock = entry_stock.get().strip()
            precio = entry_precio.get().strip()
            proveedor = entry_proveedor.get().strip()

            if not nombre or not stock or not precio or not proveedor:
                messagebox.showwarning("Campos vacíos", "Complete todos los campos obligatorios.")
                return

            # Validar que stock y precio sean números
            if not stock.isdigit():
                messagebox.showwarning("Error", "El stock debe ser un número entero.")
                return
            
            try:
                precio_float = float(precio)
            except ValueError:
                messagebox.showwarning("Error", "El precio debe ser un número válido.")
                return

            if agregar_productos(nombre, stock, precio, proveedor):
                messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado correctamente.")
                self.ver_productos()  # Actualizar la lista de productos
                # Limpiar campos
                entry_nombre.delete(0, tk.END)
                entry_stock.delete(0, tk.END)
                entry_precio.delete(0, tk.END)
                entry_proveedor.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "No se pudo agregar el producto.")
        
        tk.Button(parent, text="Crear producto", command=guardar,
                 bg='#45b7d1', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)

    def crear_tabla_inventario(self, parent, ventana):
        """Crea la tabla del inventario de productos"""
        # Crear tabla
        tree = ttk.Treeview(parent, columns=("id", "nombre", "stock", "precio", "proveedor"), show="headings")
        
        tree.heading("id", text="ID")
        tree.heading("nombre", text="Nombre")
        tree.heading("stock", text="Stock")
        tree.heading("precio", text="Precio")
        tree.heading("proveedor", text="Proveedor")
        
        tree.column("id", width=50)
        tree.column("nombre", width=150)
        tree.column("stock", width=80)
        tree.column("precio", width=80)
        tree.column("proveedor", width=120)
        
        # Cargar datos
        productos = ver_producto()
        for producto in productos:
            tree.insert("", tk.END, values=producto)
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)

    def abrir_user_view(self):
        try:
            UserApp2(self.username)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir gestión de usuarios:\n{e}")

    def cerrar_sesion(self):
        self.root.destroy()

if __name__ == "__main__":
    app2 = UserApp2("admin")