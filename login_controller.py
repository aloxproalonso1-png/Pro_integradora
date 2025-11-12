from database import crear_conexion

def validar_credenciales(usuario, password):

    conexion = crear_conexion()
    
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        # Usar nombres de columnas específicos en lugar de *
        consulta = "SELECT id FROM usuarios WHERE usuario = %s AND password = %s"
        
        cursor.execute(consulta, (usuario, password))
        result = cursor.fetchone()
        
        return result is not None
        
    except Exception as e:
        print(f"Error al validar credenciales: {e}")
        return False
    finally:
        if conexion:
            conexion.close()