# citas_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
from citas_controller import (
    agregar_cita,
    obtener_citas_hoy,
    obtener_citas_futuras,
    buscar_citas_por_nombre,
    buscar_citas_por_telefono,
    actualizar_estado_cita,
    eliminar_cita,
    obtener_cita_por_id,
    obtener_servicios_disponibles,
    generar_horas_disponibles,
    iniciar_sistema_notificaciones,
    detener_sistema_notificaciones
)

class CitasView:
    def __init__(self, root):
        self.root = root
        self.root.title("Agenda de Citas - Barbería Bravo")
        
        # Pantalla completa
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        # Iniciar sistema de notificaciones
        self.iniciar_notificaciones()
        
        self.crear_interfaz()
        self.cargar_citas_hoy()
    
    def iniciar_notificaciones(self):
        """Inicia el sistema de notificaciones"""
        def mostrar_notificacion(mensaje):
            # Mostrar notificación en una ventana emergente
            ventana_notif = tk.Toplevel(self.root)
            ventana_notif.title("🔔 Recordatorio de Cita")
            ventana_notif.geometry("400x150")
            ventana_notif.configure(bg='#fffacd')
            
            # Centrar ventana
            ventana_notif.transient(self.root)
            ventana_notif.grab_set()
            
            tk.Label(ventana_notif, text="⏰ RECORDATORIO DE CITA", 
                    font=('Arial', 14, 'bold'), bg='#fffacd').pack(pady=10)
            
            tk.Label(ventana_notif, text=mensaje, 
                    font=('Arial', 11), bg='#fffacd', wraplength=350).pack(pady=10)
            
            tk.Button(ventana_notif, text="Aceptar", 
                     command=ventana_notif.destroy,
                     bg='#4CAF50', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)
            
            # Hacer sonar (simulado)
            self.root.bell()
        
        # Iniciar sistema en segundo plano
        iniciar_sistema_notificaciones(mostrar_notificacion)
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Encabezado con botones de control
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📅 Agenda de Citas - Barbería Bravo", 
                font=("Arial", 20, "bold"), bg='#f0f0f0').pack(side='left')
        
        # Botones de control
        control_frame = tk.Frame(header_frame, bg='#f0f0f0')
        control_frame.pack(side='right')
        
        btn_nueva_cita = tk.Button(control_frame, text="Nueva Cita", width=15,
                                  command=self.mostrar_formulario_cita,
                                  bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        btn_nueva_cita.pack(side='left', padx=5)
        
        btn_volver = tk.Button(control_frame, text="Volver al Menú", width=15,
                              command=self.volver_menu_principal,
                              bg='#3498db', fg='white', font=('Arial', 10, 'bold'))
        btn_volver.pack(side='left', padx=5)
        
        btn_salir_pantalla = tk.Button(control_frame, text="Salir Pantalla Completa", width=18,
                                      command=self.salir_pantalla_completa,
                                      bg='#f39c12', fg='white', font=('Arial', 10, 'bold'))
        btn_salir_pantalla.pack(side='left', padx=5)
        
        btn_salir_sistema = tk.Button(control_frame, text="Salir Sistema", width=15,
                                     command=self.salir_sistema,
                                     bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'))
        btn_salir_sistema.pack(side='left', padx=5)
        
        # Frame de búsqueda
        buscar_frame = tk.Frame(main_frame, bg='#f0f0f0')
        buscar_frame.pack(fill='x', pady=10)
        
        tk.Label(buscar_frame, text="Buscar por:", bg='#f0f0f0', 
                font=('Arial', 10)).pack(side='left', padx=5)
        
        self.buscar_var = tk.StringVar()
        self.buscar_entry = tk.Entry(buscar_frame, textvariable=self.buscar_var, 
                                    width=30, font=('Arial', 10))
        self.buscar_entry.pack(side='left', padx=5)
        
        self.buscar_tipo = tk.StringVar(value="nombre")
        buscar_opciones = ttk.Combobox(buscar_frame, textvariable=self.buscar_tipo, 
                                      values=["nombre", "teléfono"], width=10, state="readonly")
        buscar_opciones.pack(side='left', padx=5)
        
        btn_buscar = tk.Button(buscar_frame, text="🔍 Buscar", width=10,
                              command=self.buscar_citas,
                              bg='#45b7d1', fg='white', font=('Arial', 9, 'bold'))
        btn_buscar.pack(side='left', padx=5)
        
        btn_limpiar = tk.Button(buscar_frame, text="Limpiar", width=10,
                               command=self.cargar_citas_hoy,
                               bg='#96ceb4', fg='white', font=('Arial', 9, 'bold'))
        btn_limpiar.pack(side='left', padx=5)
        
        # Frame de filtros
        filtros_frame = tk.Frame(main_frame, bg='#f0f0f0')
        filtros_frame.pack(fill='x', pady=10)
        
        tk.Label(filtros_frame, text="Mostrar:", bg='#f0f0f0', 
                font=('Arial', 10)).pack(side='left', padx=5)
        
        btn_hoy = tk.Button(filtros_frame, text="Citas de Hoy", width=12,
                           command=self.cargar_citas_hoy,
                           bg='#ff9a76', fg='white', font=('Arial', 9, 'bold'))
        btn_hoy.pack(side='left', padx=5)
        
        btn_futuras = tk.Button(filtros_frame, text="Citas Futuras", width=12,
                               command=self.cargar_citas_futuras,
                               bg='#4ecdc4', fg='white', font=('Arial', 9, 'bold'))
        btn_futuras.pack(side='left', padx=5)
        
        # Frame de citas
        citas_frame = tk.LabelFrame(main_frame, text="📋 Citas Programadas", 
                                   font=("Arial", 12, "bold"), bg='#f0f0f0')
        citas_frame.pack(fill='both', expand=True, pady=10)
        
        # Crear tabla de citas
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#4ecdc4')
        style.configure("Treeview", font=('Arial', 9), rowheight=25)
        
        columns = ("id", "nombre", "telefono", "fecha", "hora", "servicio", "estado")
        self.tree = ttk.Treeview(citas_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre del Cliente")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("servicio", text="Servicio")
        self.tree.heading("estado", text="Estado")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=150, anchor="w")
        self.tree.column("telefono", width=100, anchor="center")
        self.tree.column("fecha", width=100, anchor="center")
        self.tree.column("hora", width=80, anchor="center")
        self.tree.column("servicio", width=120, anchor="center")
        self.tree.column("estado", width=100, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(citas_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind para selección
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_cita)
        
        # Frame de botones de acción
        acciones_frame = tk.Frame(main_frame, bg='#f0f0f0')
        acciones_frame.pack(fill='x', pady=10)
        
        btn_confirmar = tk.Button(acciones_frame, text="✅ Confirmar Cita", width=15,
                                 command=self.confirmar_cita,
                                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        btn_confirmar.pack(side='left', padx=5)
        
        btn_completar = tk.Button(acciones_frame, text="✓ Completar", width=15,
                                 command=self.completar_cita,
                                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'))
        btn_completar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(acciones_frame, text="❌ Cancelar", width=15,
                                command=self.cancelar_cita,
                                bg='#ff6b6b', fg='white', font=('Arial', 10, 'bold'))
        btn_cancelar.pack(side='left', padx=5)
        
        btn_eliminar = tk.Button(acciones_frame, text="🗑️ Eliminar", width=15,
                                command=self.eliminar_cita_seleccionada,
                                bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'))
        btn_eliminar.pack(side='left', padx=5)
        
        btn_actualizar = tk.Button(acciones_frame, text="🔄 Actualizar", width=15,
                                  command=self.cargar_citas_hoy,
                                  bg='#f39c12', fg='white', font=('Arial', 10, 'bold'))
        btn_actualizar.pack(side='right', padx=5)
    
    def cargar_citas_hoy(self):
        """Carga las citas de hoy"""
        self.limpiar_tabla()
        citas = obtener_citas_hoy()
        self.mostrar_citas(citas)
    
    def cargar_citas_futuras(self):
        """Carga todas las citas futuras"""
        self.limpiar_tabla()
        citas = obtener_citas_futuras()
        self.mostrar_citas(citas)
    
    def buscar_citas(self):
        """Busca citas según el criterio"""
        termino = self.buscar_var.get().strip()
        if not termino:
            messagebox.showwarning("Advertencia", "Ingrese un término de búsqueda")
            return
        
        self.limpiar_tabla()
        
        if self.buscar_tipo.get() == "nombre":
            citas = buscar_citas_por_nombre(termino)
        else:
            citas = buscar_citas_por_telefono(termino)
        
        self.mostrar_citas(citas)
    
    def mostrar_citas(self, citas):
        """Muestra las citas en la tabla"""
        for cita in citas:
            estado = cita[6]
            color_estado = {
                'pendiente': 'orange',
                'confirmada': 'green',
                'completada': 'blue',
                'cancelada': 'red'
            }.get(estado, 'black')
            
            self.tree.insert("", tk.END, values=(
                cita[0],  # id_cita
                cita[1],  # nombre_cliente
                cita[2],  # telefono
                cita[3],  # fecha_cita
                cita[4],  # hora_cita
                cita[5] or "No especificado",  # servicio
                estado
            ), tags=(estado,))
        
        # Configurar colores para los estados
        self.tree.tag_configure('pendiente', foreground='orange')
        self.tree.tag_configure('confirmada', foreground='green')
        self.tree.tag_configure('completada', foreground='blue')
        self.tree.tag_configure('cancelada', foreground='red')
    
    def limpiar_tabla(self):
        """Limpia la tabla de citas"""
        for row in self.tree.get_children():
            self.tree.delete(row)
    
    def seleccionar_cita(self, event):
        """Maneja la selección de una cita"""
        pass  # La selección se maneja en las funciones de acción
    
    def mostrar_formulario_cita(self):
        """Muestra el formulario para agendar nueva cita"""
        self.ventana_cita = tk.Toplevel(self.root)
        self.ventana_cita.title("📝 Agendar Nueva Cita")
        self.ventana_cita.geometry("500x500")
        self.ventana_cita.configure(bg='#f0f0f0')
        self.ventana_cita.transient(self.root)
        self.ventana_cita.grab_set()
        
        # Frame principal
        frame = tk.Frame(self.ventana_cita, bg='#f0f0f0', padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text="AGENDAR NUEVA CITA", font=('Arial', 16, 'bold'),
                bg='#f0f0f0').pack(pady=(0, 20))
        
        # Campos del formulario
        campos_frame = tk.Frame(frame, bg='#f0f0f0')
        campos_frame.pack(fill='both', expand=True)
        
        # Nombre
        tk.Label(campos_frame, text="Nombre del Cliente:", bg='#f0f0f0',
                font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=10)
        self.nombre_var = tk.StringVar()
        tk.Entry(campos_frame, textvariable=self.nombre_var, width=30,
                font=('Arial', 10)).grid(row=0, column=1, pady=10, padx=10)
        
        # Teléfono
        tk.Label(campos_frame, text="Teléfono:", bg='#f0f0f0',
                font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=10)
        self.telefono_var = tk.StringVar()
        tk.Entry(campos_frame, textvariable=self.telefono_var, width=30,
                font=('Arial', 10)).grid(row=1, column=1, pady=10, padx=10)
        
        # Fecha
        tk.Label(campos_frame, text="Fecha:", bg='#f0f0f0',
                font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=10)
        self.fecha_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        tk.Entry(campos_frame, textvariable=self.fecha_var, width=30,
                font=('Arial', 10)).grid(row=2, column=1, pady=10, padx=10)
        tk.Button(campos_frame, text="Hoy", command=self.establecer_fecha_hoy,
                 bg='#45b7d1', fg='white', font=('Arial', 8)).grid(row=2, column=2, padx=5)
        
        # Hora
        tk.Label(campos_frame, text="Hora:", bg='#f0f0f0',
                font=('Arial', 10)).grid(row=3, column=0, sticky='w', pady=10)
        
        self.hora_var = tk.StringVar()
        self.combo_hora = ttk.Combobox(campos_frame, textvariable=self.hora_var,
                                      width=27, state="readonly")
        self.combo_hora.grid(row=3, column=1, pady=10, padx=10)
        
        # Actualizar horas cuando cambia la fecha
        self.fecha_var.trace('w', lambda *args: self.actualizar_horas_disponibles())
        self.actualizar_horas_disponibles()
        
        # Servicio
        tk.Label(campos_frame, text="Servicio:", bg='#f0f0f0',
                font=('Arial', 10)).grid(row=4, column=0, sticky='w', pady=10)
        
        servicios = obtener_servicios_disponibles()
        self.servicio_var = tk.StringVar()
        self.combo_servicio = ttk.Combobox(campos_frame, textvariable=self.servicio_var,
                                          values=servicios, width=27)
        self.combo_servicio.grid(row=4, column=1, pady=10, padx=10)
        
        # Notas
        tk.Label(campos_frame, text="Notas:", bg='#f0f0f0',
                font=('Arial', 10)).grid(row=5, column=0, sticky='nw', pady=10)
        self.notas_text = tk.Text(campos_frame, width=30, height=4,
                                 font=('Arial', 10))
        self.notas_text.grid(row=5, column=1, pady=10, padx=10)
        
        # Botones
        botones_frame = tk.Frame(frame, bg='#f0f0f0')
        botones_frame.pack(pady=20)
        
        tk.Button(botones_frame, text="Agendar Cita", width=15,
                 command=self.guardar_cita,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=10)
        
        tk.Button(botones_frame, text="Cancelar", width=15,
                 command=self.ventana_cita.destroy,
                 bg='#ff6b6b', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=10)
    
    def establecer_fecha_hoy(self):
        """Establece la fecha actual en el formulario"""
        self.fecha_var.set(datetime.now().strftime('%Y-%m-%d'))
    
    def actualizar_horas_disponibles(self):
        """Actualiza las horas disponibles para la fecha seleccionada"""
        fecha = self.fecha_var.get()
        if fecha:
            horas = generar_horas_disponibles(fecha)
            self.combo_hora['values'] = horas
            if horas:
                self.combo_hora.set(horas[0])
    
    def guardar_cita(self):
        """Guarda la nueva cita"""
        nombre = self.nombre_var.get().strip()
        telefono = self.telefono_var.get().strip()
        fecha = self.fecha_var.get().strip()
        hora = self.hora_var.get().strip()
        servicio = self.servicio_var.get().strip()
        notas = self.notas_text.get("1.0", tk.END).strip()
        
        # Validaciones
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        if not telefono:
            messagebox.showwarning("Advertencia", "El teléfono es obligatorio")
            return
        
        if not fecha:
            messagebox.showwarning("Advertencia", "La fecha es obligatoria")
            return
        
        if not hora:
            messagebox.showwarning("Advertencia", "La hora es obligatoria")
            return
        
        # Validar formato de fecha
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Advertencia", "Formato de fecha inválido. Use YYYY-MM-DD")
            return
        
        # Validar que la fecha no sea en el pasado
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        hoy = datetime.now().date()
        if fecha_obj.date() < hoy:
            messagebox.showwarning("Advertencia", "No se pueden agendar citas en fechas pasadas")
            return
        
        # Agregar cita
        if agregar_cita(nombre, telefono, fecha, hora, servicio if servicio else None, notas if notas else None):
            messagebox.showinfo("Éxito", f"Cita agendada exitosamente para {nombre} el {fecha} a las {hora}")
            self.ventana_cita.destroy()
            self.cargar_citas_hoy()
        else:
            messagebox.showerror("Error", "No se pudo agendar la cita. Verifique la disponibilidad.")
    
    def confirmar_cita(self):
        """Confirma la cita seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una cita para confirmar")
            return
        
        item = self.tree.item(seleccion[0])
        id_cita = item['values'][0]
        nombre_cliente = item['values'][1]
        
        respuesta = messagebox.askyesno("Confirmar", f"¿Confirmar cita con {nombre_cliente}?")
        if respuesta:
            if actualizar_estado_cita(id_cita, 'confirmada'):
                messagebox.showinfo("Éxito", "Cita confirmada")
                self.cargar_citas_hoy()
            else:
                messagebox.showerror("Error", "No se pudo confirmar la cita")
    
    def completar_cita(self):
        """Marca la cita como completada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una cita para marcar como completada")
            return
        
        item = self.tree.item(seleccion[0])
        id_cita = item['values'][0]
        nombre_cliente = item['values'][1]
        
        respuesta = messagebox.askyesno("Completar", f"¿Marcar cita con {nombre_cliente} como completada?")
        if respuesta:
            if actualizar_estado_cita(id_cita, 'completada'):
                messagebox.showinfo("Éxito", "Cita marcada como completada")
                self.cargar_citas_hoy()
            else:
                messagebox.showerror("Error", "No se pudo completar la cita")
    
    def cancelar_cita(self):
        """Cancela la cita seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una cita para cancelar")
            return
        
        item = self.tree.item(seleccion[0])
        id_cita = item['values'][0]
        nombre_cliente = item['values'][1]
        
        respuesta = messagebox.askyesno("Cancelar", f"¿Cancelar cita con {nombre_cliente}?")
        if respuesta:
            if actualizar_estado_cita(id_cita, 'cancelada'):
                messagebox.showinfo("Éxito", "Cita cancelada")
                self.cargar_citas_hoy()
            else:
                messagebox.showerror("Error", "No se pudo cancelar la cita")
    
    def eliminar_cita_seleccionada(self):
        """Elimina la cita seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una cita para eliminar")
            return
        
        item = self.tree.item(seleccion[0])
        id_cita = item['values'][0]
        nombre_cliente = item['values'][1]
        
        respuesta = messagebox.askyesno("Eliminar", f"¿Eliminar permanentemente la cita de {nombre_cliente}?")
        if respuesta:
            if eliminar_cita(id_cita):
                messagebox.showinfo("Éxito", "Cita eliminada")
                self.cargar_citas_hoy()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la cita")
    
    def volver_menu_principal(self):
        """Vuelve al menú principal"""
        detener_sistema_notificaciones()
        self.root.destroy()
        
        # Importar y abrir el punto de venta
        try:
            from productos_viw import UserApp2
            root = tk.Tk()
            app = UserApp2("admin")  # O el usuario actual
            root.mainloop()
        except ImportError:
            messagebox.showinfo("Info", "Regresando al sistema principal")
    
    def salir_pantalla_completa(self):
        """Sale del modo pantalla completa"""
        self.root.attributes('-fullscreen', False)
        self.root.geometry("1000x700")
    
    def salir_sistema(self):
        """Cierra completamente la aplicación"""
        detener_sistema_notificaciones()
        if messagebox.askyesno("Salir del Sistema", "¿Está seguro de que desea salir completamente del sistema?"):
            self.root.quit()
            self.root.destroy()
    
    def __del__(self):
        """Destructor - asegura que las notificaciones se detengan"""
        detener_sistema_notificaciones()

if __name__ == "__main__":
    root = tk.Tk()
    app = CitasView(root)
    root.mainloop()