from database import crear_conexion

def validar_credenciales(usuario, password):
    conexion = crear_conexion()
    
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
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

def obtener_tipo_usuario(usuario):
    """
    Retorna el tipo de usuario desde la columna 'Rol' en la base de datos
    Versión mejorada que detecta roles de jefe automáticamente
    """
    conexion = crear_conexion()
    
    if not conexion:
        return 'trabajador'
    
    try:
        cursor = conexion.cursor()
        consulta = "SELECT Rol FROM usuarios WHERE usuario = %s"
        
        cursor.execute(consulta, (usuario,))
        result = cursor.fetchone()
        
        if result and result[0]:
            rol = result[0].lower()
            
            # Palabras clave que indican que es jefe
            palabras_clave_jefe = [
                'admin', 'administrador', 'jefe', 'gerente', 'manager', 
                'supervisor', 'dueño', 'propietario', 'boss', 'director'
            ]
            
            # Verificar si el rol contiene alguna palabra clave de jefe
            for palabra in palabras_clave_jefe:
                if palabra in rol:
                    return 'jefe'
            
            # Si no encuentra palabras clave, es trabajador
            return 'trabajador'
        else:
            return 'trabajador'
        
    except Exception as e:
        print(f"Error al obtener tipo de usuario: {e}")
        return 'trabajador'
    finally:
        if conexion:
            conexion.close()