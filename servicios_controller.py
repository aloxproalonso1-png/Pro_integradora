import mysql.connector
from database import crear_conexion  

def ver_servicios():
    """Obtiene todos los servicios de la base de datos"""
    connection = crear_conexion()
    servicios = []
    
    try:
        with connection.cursor() as cursor:
            # CORREGIDO: usar 'duracion' sin acento
            sql = "SELECT id_servicio, nombre_servicio, descripcion, duracion, precio FROM servicios"
            cursor.execute(sql)
            servicios = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al obtener servicios: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return servicios

def agregar_servicio(nombre, descripcion, duracion, precio):
    """Agrega un nuevo servicio a la base de datos"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            # CORREGIDO: usar 'duracion' sin acento
            sql = """INSERT INTO servicios 
                     (nombre_servicio, descripcion, duracion, precio) 
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (nombre, descripcion, duracion, precio))
            connection.commit()
            print("✅ Servicio agregado exitosamente")
            return True
            
    except Exception as e:
        print(f"❌ Error al agregar servicio: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def editar_servicio(id_servicio, nombre, descripcion, duracion, precio):
    """Edita un servicio existente"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            # CORREGIDO: usar 'duracion' sin acento
            sql = """UPDATE servicios 
                     SET nombre_servicio = %s, descripcion = %s, duracion = %s, precio = %s 
                     WHERE id_servicio = %s"""
            cursor.execute(sql, (nombre, descripcion, duracion, precio, id_servicio))
            connection.commit()
            print("✅ Servicio editado exitosamente")
            return True
    except Exception as e:
        print(f"❌ Error al editar servicio: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def eliminar_servicio(id_servicio):
    """Elimina un servicio de la base de datos"""
    connection = crear_conexion()
    
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM servicios WHERE id_servicio = %s"
            cursor.execute(sql, (id_servicio,))
            connection.commit()
            print("✅ Servicio eliminado exitosamente")
            return True
    except Exception as e:
        print(f"❌ Error al eliminar servicio: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def obtener_servicio_por_id(id_servicio):
    """Obtiene un servicio específico por su ID"""
    connection = crear_conexion()
    servicio = None
    
    try:
        with connection.cursor() as cursor:
            # CORREGIDO: usar 'duracion' sin acento
            sql = """SELECT id_servicio, nombre_servicio, descripcion, 
                            duracion, precio 
                     FROM servicios 
                     WHERE id_servicio = %s"""
            cursor.execute(sql, (id_servicio,))
            servicio = cursor.fetchone()
    except Exception as e:
        print(f"❌ Error al obtener servicio: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return servicio