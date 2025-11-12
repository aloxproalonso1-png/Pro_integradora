import tkinter as tk
from tkinter import ttk, messagebox
from Stock_controller import (
    obtener_productos, 
    obtener_producto_por_id, 
    obtener_productos_stock_bajo,
    agregar_producto, 
    actualizar_producto, 
    actualizar_stock,
    eliminar_producto,
    buscar_productos
)

class StockView:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Stock - Barbería Bravo")
        self.root.geometry("1000x600")
        
        # Variables
        self.buscar_var = tk.StringVar()
        
        self.crear_interfaz()
        self.actualizar_lista()
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Gestión de Inventario", font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Frame de búsqueda
        buscar_frame = ttk.Frame(main_frame)
        buscar_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        buscar_frame.columnconfigure(1, weight=1)
        
        ttk.Label(buscar_frame, text="Buscar:").grid(row=0, column=0, padx=(0, 10))
        ttk.Entry(buscar_frame, textvariable=self.buscar_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(buscar_frame, text="Buscar", command=self.buscar_productos).grid(row=0, column=2, padx=(10, 0))
        ttk.Button(buscar_frame, text="Mostrar Todos", command=self.actualizar_lista).grid(row=0, column=3, padx=(10, 0))
        
        # Treeview para mostrar productos
        columns = ('ID', 'Nombre', 'Stock', 'Precio', 'Proveedor')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nombre', text='Nombre del Producto')
        self.tree.heading('Stock', text='Stock')
        self.tree.heading('Precio', text='Precio')
        self.tree.heading('Proveedor', text='Proveedor')
        
        self.tree.column('ID', width=50)
        self.tree.column('Nombre', width=200)
        self.tree.column('Stock', width=80)
        self.tree.column('Precio', width=80)
        self.tree.column('Proveedor', width=150)
        
        self.tree.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=2, column=4, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame de botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(botones_frame, text="Agregar Producto", command=self.mostrar_agregar_producto).grid(row=0, column=0, padx=5)
        ttk.Button(botones_frame, text="Editar Producto", command=self.mostrar_editar_producto).grid(row=0, column=1, padx=5)
        ttk.Button(botones_frame, text="Eliminar Producto", command=self.mostrar_eliminar_producto).grid(row=0, column=2, padx=5)
        ttk.Button(botones_frame, text="Actualizar Stock", command=self.mostrar_actualizar_stock).grid(row=0, column=3, padx=5)
        ttk.Button(botones_frame, text="Stock Bajo", command=self.mostrar_stock_bajo).grid(row=0, column=4, padx=5)
        ttk.Button(botones_frame, text="Actualizar Lista", command=self.actualizar_lista).grid(row=0, column=5, padx=5)
        
        # Bind double click para editar
        self.tree.bind('<Double-1>', self.on_double_click)
    
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
                f"${producto['precio']}",
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
                f"${producto['precio']}",
                producto['proveedor']
            ))
    
    def on_double_click(self, event):
        """Al hacer doble click en un producto, lo edita"""
        self.mostrar_editar_producto()
    
    def mostrar_agregar_producto(self):
        """Ventana para agregar nuevo producto"""
        self.ventana_agregar = tk.Toplevel(self.root)
        self.ventana_agregar.title("Agregar Producto")
        self.ventana_agregar.geometry("400x300")
        self.ventana_agregar.transient(self.root)
        self.ventana_agregar.grab_set()
        
        self.crear_formulario(self.ventana_agregar, self.guardar_nuevo_producto)
    
    def mostrar_editar_producto(self):
        """Ventana para editar producto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto para editar")
            return
        
        item = self.tree.item(seleccion[0])
        id_producto = item['values'][0]
        
        producto = obtener_producto_por_id(id_producto)
        if not producto:
            messagebox.showerror("Error", "No se pudo obtener la información del producto")
            return
        
        self.ventana_editar = tk.Toplevel(self.root)
        self.ventana_editar.title("Editar Producto")
        self.ventana_editar.geometry("400x300")
        self.ventana_editar.transient(self.root)
        self.ventana_editar.grab_set()
        
        self.crear_formulario(self.ventana_editar, self.guardar_edicion_producto, producto)
    
    def crear_formulario(self, ventana, comando_guardar, producto=None):
        """Crea el formulario para agregar/editar productos"""
        frame = ttk.Frame(ventana, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Variables del formulario
        nombre_var = tk.StringVar(value=producto['nombre_producto'] if producto else "")
        stock_var = tk.StringVar(value=str(producto['stock']) if producto else "0")
        precio_var = tk.StringVar(value=str(producto['precio']) if producto else "0")
        proveedor_var = tk.StringVar(value=producto['proveedor'] if producto else "")
        
        # Campos del formulario
        ttk.Label(frame, text="Nombre del Producto:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_nombre = ttk.Entry(frame, textvariable=nombre_var, width=30)
        entry_nombre.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(frame, text="Stock:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_stock = ttk.Entry(frame, textvariable=stock_var, width=30)
        entry_stock.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(frame, text="Precio:").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_precio = ttk.Entry(frame, textvariable=precio_var, width=30)
        entry_precio.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(frame, text="Proveedor:").grid(row=3, column=0, sticky=tk.W, pady=5)
        entry_proveedor = ttk.Entry(frame, textvariable=proveedor_var, width=30)
        entry_proveedor.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Frame de botones
        botones_frame = ttk.Frame(frame)
        botones_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        if producto:
            ttk.Button(botones_frame, text="Guardar Cambios", 
                      command=lambda: comando_guardar(producto['id_producto'], nombre_var.get(), stock_var.get(), precio_var.get(), proveedor_var.get())).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(botones_frame, text="Agregar Producto", 
                      command=lambda: comando_guardar(nombre_var.get(), stock_var.get(), precio_var.get(), proveedor_var.get())).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botones_frame, text="Cancelar", command=ventana.destroy).pack(side=tk.LEFT, padx=5)
        
        frame.columnconfigure(1, weight=1)
    
    def guardar_nuevo_producto(self, nombre, stock, precio, proveedor):
        """Guarda un nuevo producto"""
        if not nombre or not proveedor:
            messagebox.showwarning("Advertencia", "Nombre y proveedor son obligatorios")
            return
        
        try:
            stock_int = int(stock)
            precio_int = int(precio)
            
            if agregar_producto(nombre, stock_int, precio_int, proveedor):
                messagebox.showinfo("Éxito", "Producto agregado correctamente")
                self.ventana_agregar.destroy()
                self.actualizar_lista()
            else:
                messagebox.showerror("Error", "No se pudo agregar el producto")
        except ValueError:
            messagebox.showerror("Error", "Stock y precio deben ser números válidos")
    
    def guardar_edicion_producto(self, id_producto, nombre, stock, precio, proveedor):
        """Guarda los cambios de un producto editado"""
        if not nombre or not proveedor:
            messagebox.showwarning("Advertencia", "Nombre y proveedor son obligatorios")
            return
        
        try:
            stock_int = int(stock)
            precio_int = int(precio)
            
            if actualizar_producto(id_producto, nombre, stock_int, precio_int, proveedor):
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                self.ventana_editar.destroy()
                self.actualizar_lista()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el producto")
        except ValueError:
            messagebox.showerror("Error", "Stock y precio deben ser números válidos")
    
    def mostrar_eliminar_producto(self):
        """Elimina el producto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto para eliminar")
            return
        
        item = self.tree.item(seleccion[0])
        id_producto = item['values'][0]
        nombre_producto = item['values'][1]
        
        respuesta = messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el producto: {nombre_producto}?")
        if respuesta:
            if eliminar_producto(id_producto):
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                self.actualizar_lista()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el producto")
    
    def mostrar_actualizar_stock(self):
        """Ventana para actualizar stock del producto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
        
        item = self.tree.item(seleccion[0])
        id_producto = item['values'][0]
        nombre_producto = item['values'][1]
        stock_actual = item['values'][2]
        
        self.ventana_stock = tk.Toplevel(self.root)
        self.ventana_stock.title("Actualizar Stock")
        self.ventana_stock.geometry("300x200")
        self.ventana_stock.transient(self.root)
        self.ventana_stock.grab_set()
        
        frame = ttk.Frame(self.ventana_stock, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Producto: {nombre_producto}", font=('Arial', 10, 'bold')).pack(pady=5)
        ttk.Label(frame, text=f"Stock actual: {stock_actual}").pack(pady=5)
        
        ttk.Label(frame, text="Nuevo stock:").pack(pady=10)
        nuevo_stock_var = tk.StringVar()
        entry_stock = ttk.Entry(frame, textvariable=nuevo_stock_var, width=10)
        entry_stock.pack(pady=5)
        
        botones_frame = ttk.Frame(frame)
        botones_frame.pack(pady=20)
        
        ttk.Button(botones_frame, text="Actualizar", 
                  command=lambda: self.guardar_stock(id_producto, nuevo_stock_var.get())).pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Cancelar", command=self.ventana_stock.destroy).pack(side=tk.LEFT, padx=5)
    
    def guardar_stock(self, id_producto, nuevo_stock):
        """Guarda el nuevo stock"""
        try:
            stock_int = int(nuevo_stock)
            if stock_int < 0:
                messagebox.showwarning("Advertencia", "El stock no puede ser negativo")
                return
            
            if actualizar_stock(id_producto, stock_int):
                messagebox.showinfo("Éxito", "Stock actualizado correctamente")
                self.ventana_stock.destroy()
                self.actualizar_lista()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el stock")
        except ValueError:
            messagebox.showerror("Error", "El stock debe ser un número válido")
    
    def mostrar_stock_bajo(self):
        """Muestra solo los productos con stock bajo"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        productos = obtener_productos_stock_bajo()
        if not productos:
            messagebox.showinfo("Stock Bajo", "No hay productos con stock bajo")
            self.actualizar_lista()
            return
        
        for producto in productos:
            self.tree.insert('', tk.END, values=(
                producto['id_producto'],
                producto['nombre_producto'],
                producto['stock'],
                f"${producto['precio']}",
                producto['proveedor']
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = StockView(root)
    root.mainloop()