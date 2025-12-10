# citas_controller.py
import mysql.connector
from database import crear_conexion
from datetime import datetime, timedelta
import threading
import time

def agregar_cita(nombre_cliente, telefono, fecha_cita, hora_cita, servicio=None, notas=None):
    """Agrega una nueva cita a la base de datos"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO citas 
                     (nombre_cliente, telefono, fecha_cita, hora_cita, servicio, notas, estado) 
                     VALUES (%s, %s, %s, %s, %s, %s, 'pendiente')"""
            cursor.execute(sql, (nombre_cliente, telefono, fecha_cita, hora_cita, servicio, notas))
            connection.commit()
            print(f"✅ Cita agregada - Cliente: {nombre_cliente}, Fecha: {fecha_cita}, Hora: {hora_cita}")
            return True
    except Exception as e:
        print(f"❌ Error al agregar cita: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def obtener_citas_por_fecha(fecha):
    """Obtiene todas las citas para una fecha específica"""
    connection = crear_conexion()
    citas = []
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT * FROM citas 
                     WHERE fecha_cita = %s 
                     ORDER BY hora_cita"""
            cursor.execute(sql, (fecha,))
            citas = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al obtener citas: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return citas

def obtener_citas_hoy():
    """Obtiene las citas de hoy"""
    hoy = datetime.now().strftime('%Y-%m-%d')
    return obtener_citas_por_fecha(hoy)

def obtener_citas_futuras():
    """Obtiene todas las citas futuras"""
    connection = crear_conexion()
    citas = []
    
    try:
        with connection.cursor() as cursor:
            hoy = datetime.now().strftime('%Y-%m-%d')
            sql = """SELECT * FROM citas 
                     WHERE fecha_cita >= %s 
                     AND estado IN ('pendiente', 'confirmada')
                     ORDER BY fecha_cita, hora_cita"""
            cursor.execute(sql, (hoy,))
            citas = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al obtener citas futuras: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return citas

def buscar_citas_por_nombre(nombre):
    """Busca citas por nombre del cliente"""
    connection = crear_conexion()
    citas = []
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT * FROM citas 
                     WHERE nombre_cliente LIKE %s 
                     AND estado IN ('pendiente', 'confirmada')
                     ORDER BY fecha_cita DESC"""
            cursor.execute(sql, (f"%{nombre}%",))
            citas = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al buscar citas: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return citas

def buscar_citas_por_telefono(telefono):
    """Busca citas por teléfono del cliente"""
    connection = crear_conexion()
    citas = []
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT * FROM citas 
                     WHERE telefono LIKE %s 
                     AND estado IN ('pendiente', 'confirmada')
                     ORDER BY fecha_cita DESC"""
            cursor.execute(sql, (f"%{telefono}%",))
            citas = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al buscar citas: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return citas

def actualizar_estado_cita(id_cita, nuevo_estado):
    """Actualiza el estado de una cita"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE citas SET estado = %s WHERE id_cita = %s"
            cursor.execute(sql, (nuevo_estado, id_cita))
            connection.commit()
            print(f"✅ Estado de cita {id_cita} actualizado a {nuevo_estado}")
            return True
    except Exception as e:
        print(f"❌ Error al actualizar cita: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def eliminar_cita(id_cita):
    """Elimina una cita"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM citas WHERE id_cita = %s"
            cursor.execute(sql, (id_cita,))
            connection.commit()
            print(f"✅ Cita {id_cita} eliminada")
            return True
    except Exception as e:
        print(f"❌ Error al eliminar cita: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def obtener_cita_por_id(id_cita):
    """Obtiene una cita específica por ID"""
    connection = crear_conexion()
    cita = None
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM citas WHERE id_cita = %s"
            cursor.execute(sql, (id_cita,))
            cita = cursor.fetchone()
    except Exception as e:
        print(f"❌ Error al obtener cita: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return cita

def obtener_proximas_citas():
    """Obtiene las próximas citas (próximas 2 horas)"""
    connection = crear_conexion()
    citas = []
    
    try:
        with connection.cursor() as cursor:
            ahora = datetime.now()
            dos_horas_despues = ahora + timedelta(hours=2)
            
            fecha_hoy = ahora.strftime('%Y-%m-%d')
            hora_ahora = ahora.strftime('%H:%M:%S')
            hora_limite = dos_horas_despues.strftime('%H:%M:%S')
            
            sql = """SELECT * FROM citas 
                     WHERE fecha_cita = %s 
                     AND hora_cita BETWEEN %s AND %s
                     AND estado IN ('pendiente', 'confirmada')
                     ORDER BY hora_cita"""
            cursor.execute(sql, (fecha_hoy, hora_ahora, hora_limite))
            citas = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al obtener próximas citas: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return citas

def obtener_servicios_disponibles():
    """Obtiene los servicios disponibles para las citas"""
    from servicios_controller import ver_servicios
    servicios = ver_servicios()
    return [servicio[1] for servicio in servicios]  # Retorna solo los nombres

def verificar_disponibilidad(fecha, hora):
    """Verifica si hay disponibilidad en una fecha y hora específicas"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT COUNT(*) as count FROM citas 
                     WHERE fecha_cita = %s 
                     AND hora_cita = %s
                     AND estado IN ('pendiente', 'confirmada')"""
            cursor.execute(sql, (fecha, hora))
            resultado = cursor.fetchone()
            
            # Máximo 1 cita por hora
            return resultado[0] == 0
    except Exception as e:
        print(f"❌ Error al verificar disponibilidad: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def generar_horas_disponibles(fecha):
    """Genera las horas disponibles para una fecha específica"""
    horas_base = [
        '09:00', '10:00', '11:00', '12:00', '13:00', 
        '14:00', '15:00', '16:00', '17:00', '18:00', '19:00'
    ]
    
    horas_disponibles = []
    
    for hora in horas_base:
        if verificar_disponibilidad(fecha, hora):
            horas_disponibles.append(hora)
    
    return horas_disponibles

class SistemaNotificaciones:
    """Sistema de notificaciones para citas"""
    
    def __init__(self):
        self.activo = False
        self.hilo_notificaciones = None
    
    def iniciar(self, callback_notificacion=None):
        """Inicia el sistema de notificaciones en segundo plano"""
        self.activo = True
        self.callback = callback_notificacion
        
        def monitor_citas():
            while self.activo:
                try:
                    # Verificar citas próximas (dentro de 30 minutos)
                    citas_proximas = self.obtener_citas_proximas_30_min()
                    
                    for cita in citas_proximas:
                        mensaje = f"Recordatorio: Cita con {cita[1]} a las {cita[4]}"
                        
                        if self.callback:
                            self.callback(mensaje)
                        else:
                            print(f"🔔 NOTIFICACIÓN: {mensaje}")
                    
                    # Dormir por 5 minutos antes de verificar de nuevo
                    time.sleep(300)
                    
                except Exception as e:
                    print(f"❌ Error en sistema de notificaciones: {e}")
                    time.sleep(60)
        
        self.hilo_notificaciones = threading.Thread(target=monitor_citas, daemon=True)
        self.hilo_notificaciones.start()
        print("✅ Sistema de notificaciones iniciado")
    
    def detener(self):
        """Detiene el sistema de notificaciones"""
        self.activo = False
        print("⏹️ Sistema de notificaciones detenido")
    
    def obtener_citas_proximas_30_min(self):
        """Obtiene citas que están a 30 minutos o menos"""
        connection = crear_conexion()
        citas = []
        
        try:
            with connection.cursor() as cursor:
                ahora = datetime.now()
                treinta_minutos_despues = ahora + timedelta(minutes=30)
                
                fecha_hoy = ahora.strftime('%Y-%m-%d')
                hora_ahora = ahora.strftime('%H:%M:%S')
                hora_limite = treinta_minutos_despues.strftime('%H:%M:%S')
                
                sql = """SELECT * FROM citas 
                         WHERE fecha_cita = %s 
                         AND hora_cita BETWEEN %s AND %s
                         AND estado IN ('pendiente', 'confirmada')
                         AND TIMESTAMPDIFF(MINUTE, NOW(), CONCAT(fecha_cita, ' ', hora_cita)) <= 30"""
                cursor.execute(sql, (fecha_hoy, hora_ahora, hora_limite))
                citas = cursor.fetchall()
        except Exception as e:
            print(f"❌ Error al obtener citas próximas: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()
        
        return citas

# Instancia global del sistema de notificaciones
sistema_notificaciones = SistemaNotificaciones()

def iniciar_sistema_notificaciones(callback=None):
    """Inicia el sistema de notificaciones"""
    sistema_notificaciones.iniciar(callback)

def detener_sistema_notificaciones():
    """Detiene el sistema de notificaciones"""
    sistema_notificaciones.detener()