# historial_controller.py
from database import crear_conexion
import uuid
from datetime import datetime

def guardar_venta(venta_id_gruppo, id_usuario, id_producto, nombre_servicio, cantidad, precio_unitario, subtotal):
    """Guarda una venta individual en la base de datos"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO ventas 
                     (venta_id_gruppo, id, id_producto, nombre_servicio, 
                      cantidad, precio_unitario, subtotal, fecha) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())"""
            
            valores = (
                venta_id_gruppo,
                id_usuario,
                id_producto if id_producto is not None else None,
                nombre_servicio if nombre_servicio is not None else None,
                cantidad,
                precio_unitario,
                subtotal
            )
            cursor.execute(sql, valores)
            connection.commit()
            print(f"✅ Venta guardada exitosamente (ID grupo: {venta_id_gruppo})")
            return True
            
    except Exception as e:
        print(f"❌ Error al guardar venta: {e}")
        connection.rollback()
        return False
        
    finally:
        if connection and connection.is_connected():
            connection.close()

def obtener_id_usuario(username):
    """Obtiene el ID de usuario a partir del nombre de usuario"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id FROM usuarios WHERE Usuario = %s"
            cursor.execute(sql, (username,))
            resultado = cursor.fetchone()
            
            if resultado:
                return resultado[0]  # Retorna el ID del usuario
            else:
                print(f"⚠️ Usuario '{username}' no encontrado")
                return None
                
    except Exception as e:
        print(f"❌ Error al obtener ID de usuario: {e}")
        return None
        
    finally:
        if connection and connection.is_connected():
            connection.close()

def obtener_nombre_usuario(id_usuario):
    """Obtiene el nombre de usuario a partir del ID"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT Usuario FROM usuarios WHERE id = %s"
            cursor.execute(sql, (id_usuario,))
            resultado = cursor.fetchone()
            
            if resultado:
                return resultado[0]  # Retorna el nombre de usuario
            else:
                print(f"⚠️ Usuario con ID '{id_usuario}' no encontrado")
                return "Desconocido"
                
    except Exception as e:
        print(f"❌ Error al obtener nombre de usuario: {e}")
        return "Error"
        
    finally:
        if connection and connection.is_connected():
            connection.close()

def obtener_ventas_agrupadas():
    """Obtiene todas las ventas agrupadas por venta_id_gruppo (para jefes)"""
    connection = crear_conexion()
    ventas_agrupadas = []
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT 
                        v.venta_id_gruppo,
                        v.id,
                        u.Usuario as username,
                        COUNT(*) as total_items,
                        SUM(v.subtotal) as total_venta,
                        MAX(v.fecha) as fecha
                     FROM ventas v 
                     LEFT JOIN usuarios u ON v.id = u.id 
                     GROUP BY v.venta_id_gruppo, v.id
                     ORDER BY fecha DESC"""
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            # Convertir a formato de tupla para compatibilidad
            for r in resultados:
                ventas_agrupadas.append((
                    r[0],  # venta_id_gruppo
                    r[1],  # id_usuario
                    r[2],  # username
                    r[3],  # total_items
                    float(r[4]),  # total_venta
                    r[5]   # fecha
                ))
                
    except Exception as e:
        print(f"Error al obtener ventas agrupadas: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return ventas_agrupadas

def obtener_ventas_agrupadas_por_usuario(id_usuario):
    """Obtiene las ventas agrupadas por venta_id_gruppo para un usuario específico"""
    connection = crear_conexion()
    ventas_agrupadas = []
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT 
                        v.venta_id_gruppo,
                        v.id,
                        u.Usuario as username,
                        COUNT(*) as total_items,
                        SUM(v.subtotal) as total_venta,
                        MAX(v.fecha) as fecha
                     FROM ventas v 
                     LEFT JOIN usuarios u ON v.id = u.id 
                     WHERE v.id = %s
                     GROUP BY v.venta_id_gruppo, v.id
                     ORDER BY fecha DESC"""
            cursor.execute(sql, (id_usuario,))
            resultados = cursor.fetchall()
            
            for r in resultados:
                ventas_agrupadas.append((
                    r[0],  # venta_id_gruppo
                    r[1],  # id_usuario
                    r[2],  # username
                    r[3],  # total_items
                    float(r[4]),  # total_venta
                    r[5]   # fecha
                ))
                
    except Exception as e:
        print(f"Error al obtener ventas agrupadas del usuario: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return ventas_agrupadas

def obtener_detalles_venta(venta_id_gruppo):
    """Obtiene los detalles de una venta específica"""
    connection = crear_conexion()
    detalles = []
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT 
                        v.id_venta,
                        v.venta_id_gruppo,
                        v.id_producto,
                        p.nombre as nombre_producto,
                        v.nombre_servicio,
                        v.cantidad,
                        v.precio_unitario,
                        v.subtotal
                     FROM ventas v 
                     LEFT JOIN productos p ON v.id_producto = p.id_producto
                     WHERE v.venta_id_gruppo = %s 
                     ORDER BY v.id_venta"""
            cursor.execute(sql, (venta_id_gruppo,))
            resultados = cursor.fetchall()
            
            for r in resultados:
                detalles.append((
                    r[0],  # id_venta
                    r[1],  # venta_id_gruppo
                    r[2],  # id_producto
                    r[3],  # nombre_producto
                    r[4],  # nombre_servicio
                    r[5],  # cantidad
                    float(r[6]),  # precio_unitario
                    float(r[7])   # subtotal
                ))
                
    except Exception as e:
        print(f"Error al obtener detalles de venta: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return detalles

def obtener_estadisticas_ventas():
    """Obtiene estadísticas generales de ventas"""
    connection = crear_conexion()
    estadisticas = {}
    
    try:
        with connection.cursor() as cursor:
            # Total de ventas agrupadas
            sql_total_ventas = "SELECT COUNT(DISTINCT venta_id_gruppo) FROM ventas"
            cursor.execute(sql_total_ventas)
            total_ventas = cursor.fetchone()[0] or 0
            
            # Monto total
            sql_monto_total = "SELECT SUM(subtotal) FROM ventas"
            cursor.execute(sql_monto_total)
            monto_total = cursor.fetchone()[0] or 0
            
            # Total de productos vendidos
            sql_total_productos = "SELECT SUM(cantidad) FROM ventas"
            cursor.execute(sql_total_productos)
            total_productos = cursor.fetchone()[0] or 0
            
            estadisticas = {
                'total_ventas': total_ventas,
                'monto_total': float(monto_total),
                'total_productos': total_productos
            }
            
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        estadisticas = {'total_ventas': 0, 'monto_total': 0.0, 'total_productos': 0}
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return estadisticas

def obtener_estadisticas_usuario(id_usuario):
    """Obtiene estadísticas de ventas para un usuario específico"""
    connection = crear_conexion()
    estadisticas = {}
    
    try:
        with connection.cursor() as cursor:
            # Total de ventas agrupadas del usuario
            sql_total_ventas = "SELECT COUNT(DISTINCT venta_id_gruppo) FROM ventas WHERE id = %s"
            cursor.execute(sql_total_ventas, (id_usuario,))
            total_ventas = cursor.fetchone()[0] or 0
            
            # Monto total del usuario
            sql_monto_total = "SELECT SUM(subtotal) FROM ventas WHERE id = %s"
            cursor.execute(sql_monto_total, (id_usuario,))
            monto_total = cursor.fetchone()[0] or 0
            
            # Total de productos vendidos por el usuario
            sql_total_productos = "SELECT SUM(cantidad) FROM ventas WHERE id = %s"
            cursor.execute(sql_total_productos, (id_usuario,))
            total_productos = cursor.fetchone()[0] or 0
            
            estadisticas = {
                'total_ventas': total_ventas,
                'monto_total': float(monto_total),
                'total_productos': total_productos
            }
            
    except Exception as e:
        print(f"Error al obtener estadísticas del usuario: {e}")
        estadisticas = {'total_ventas': 0, 'monto_total': 0.0, 'total_productos': 0}
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return estadisticas

def obtener_ventas_por_rango_fechas(fecha_inicio, fecha_fin):
    """Obtiene ventas dentro de un rango de fechas"""
    connection = crear_conexion()
    ventas_agrupadas = []
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT 
                        v.venta_id_gruppo,
                        v.id,
                        u.Usuario as username,
                        COUNT(*) as total_items,
                        SUM(v.subtotal) as total_venta,
                        MAX(v.fecha) as fecha
                     FROM ventas v 
                     LEFT JOIN usuarios u ON v.id = u.id 
                     WHERE v.fecha BETWEEN %s AND %s
                     GROUP BY v.venta_id_gruppo, v.id
                     ORDER BY fecha DESC"""
            cursor.execute(sql, (fecha_inicio, fecha_fin))
            resultados = cursor.fetchall()
            
            for r in resultados:
                ventas_agrupadas.append((
                    r[0],  # venta_id_gruppo
                    r[1],  # id_usuario
                    r[2],  # username
                    r[3],  # total_items
                    float(r[4]),  # total_venta
                    r[5]   # fecha
                ))
                
    except Exception as e:
        print(f"Error al obtener ventas por fecha: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return ventas_agrupadas

def eliminar_venta(venta_id_gruppo):
    """Elimina todas las transacciones de una venta agrupada"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM ventas WHERE venta_id_gruppo = %s"
            cursor.execute(sql, (venta_id_gruppo,))
            connection.commit()
            print(f"✅ Venta {venta_id_gruppo} eliminada exitosamente")
            return True
            
    except Exception as e:
        print(f"❌ Error al eliminar venta: {e}")
        connection.rollback()
        return False
        
    finally:
        if connection and connection.is_connected():
            connection.close()

def generar_id_venta():
    """Genera un ID único para agrupar ventas"""
    return f"VENTA-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

# Función auxiliar para debugging
def contar_ventas_totales():
    """Cuenta el total de ventas en la base de datos"""
    connection = crear_conexion()
    total = 0
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM ventas"
            cursor.execute(sql)
            total = cursor.fetchone()[0]
            print(f"📊 Total de registros en tabla ventas: {total}")
            
    except Exception as e:
        print(f"Error al contar ventas: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return total

# Prueba de las funciones (opcional)
if __name__ == "__main__":
    print("🔧 Probando funciones del historial controller...")
    
    # Test: Obtener ID de usuario
    id_usuario = obtener_id_usuario("admin")
    if id_usuario:
        print(f"ID del usuario admin: {id_usuario}")
    
    # Test: Estadísticas
    stats = obtener_estadisticas_ventas()
    print(f"Estadísticas: {stats}")
    
    # Test: Contar ventas
    total = contar_ventas_totales()
    print(f"Total ventas: {total}")
    
    # Test: Generar ID de venta
    venta_id = generar_id_venta()
    print(f"ID de venta generado: {venta_id}")