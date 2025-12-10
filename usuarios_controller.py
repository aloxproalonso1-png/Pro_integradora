from database import crear_conexion
import hashlib

def obtener_usuarios():
    """Obtiene todos los usuarios"""
    conexion = crear_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Id, Usuario, Rol, fecha FROM usuarios ORDER BY fecha DESC")
        resultado = cursor.fetchall()
        return resultado
    except Exception as e:
        print(f"Error al obtener usuarios. Tipo de error: {e}")
        return []
    finally:
        if conexion:
            conexion.close()

def obtener_usuario_por_id(id_usuario):
    """Obtiene un usuario específico por ID"""
    conexion = crear_conexion()
    if not conexion:
        return None
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Id, Usuario, Rol, fecha FROM usuarios WHERE Id = %s", (id_usuario,))
        resultado = cursor.fetchone()
        return resultado
    except Exception as e:
        print(f"Error al obtener usuario por ID. Tipo de error: {e}")
        return None
    finally:
        if conexion:
            conexion.close()

def obtener_usuario_por_nombre(usuario):
    """Obtiene un usuario por nombre de usuario"""
    conexion = crear_conexion()
    if not conexion:
        return None
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Id, Usuario, password, Rol, fecha FROM usuarios WHERE Usuario = %s", (usuario,))
        resultado = cursor.fetchone()
        return resultado
    except Exception as e:
        print(f"Error al obtener usuario por nombre. Tipo de error: {e}")
        return None
    finally:
        if conexion:
            conexion.close()

def verificar_credenciales(usuario, password):
    """Verifica las credenciales de un usuario"""
    conexion = crear_conexion()
    if not conexion:
        return None
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Id, Usuario, password, Rol FROM usuarios WHERE Usuario = %s", (usuario,))
        resultado = cursor.fetchone()
        
        if resultado and verificar_password(password, resultado['password']):
            return resultado
        return None
    except Exception as e:
        print(f"Error al verificar credenciales. Tipo de error: {e}")
        return None
    finally:
        if conexion:
            conexion.close()

def hash_password(password):
    """Genera el hash de una contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_password(password, password_hash):
    """Verifica si la contraseña coincide con el hash"""
    return hash_password(password) == password_hash

def agregar_usuario(usuario, password, rol):
    """Agrega un nuevo usuario"""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        # Verificar si el usuario ya existe
        if obtener_usuario_por_nombre(usuario):
            return "usuario_existe"
        
        password_hash = hash_password(password)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (Usuario, password, Rol) VALUES (%s, %s, %s)", 
                      (usuario, password_hash, rol))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al agregar usuario. Tipo de error: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def actualizar_usuario(id_usuario, usuario, rol, cambiar_password=False, nueva_password=None):
    """Actualiza un usuario existente"""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        
        if cambiar_password and nueva_password:
            password_hash = hash_password(nueva_password)
            cursor.execute("UPDATE usuarios SET Usuario = %s, Rol = %s, password = %s WHERE Id = %s", 
                          (usuario, rol, password_hash, id_usuario))
        else:
            cursor.execute("UPDATE usuarios SET Usuario = %s, Rol = %s WHERE Id = %s", 
                          (usuario, rol, id_usuario))
        
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar usuario. Tipo de error: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def eliminar_usuario(id_usuario):
    """Elimina un usuario"""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        # Verificar que no sea el último administrador
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE Rol = 'admin'")
        resultado = cursor.fetchone()
        
        if resultado['count'] <= 1:
            cursor.execute("SELECT Rol FROM usuarios WHERE Id = %s", (id_usuario,))
            usuario = cursor.fetchone()
            if usuario and usuario['Rol'] == 'admin':
                return "ultimo_admin"
        
        cursor.execute("DELETE FROM usuarios WHERE Id = %s", (id_usuario,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario. Tipo de error: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def buscar_usuarios(termino_busqueda):
    """Busca usuarios por nombre o rol"""
    conexion = crear_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Id, Usuario, Rol, fecha FROM usuarios WHERE Usuario LIKE %s OR Rol LIKE %s", 
                      (f"%{termino_busqueda}%", f"%{termino_busqueda}%"))
        resultado = cursor.fetchall()
        return resultado
    except Exception as e:
        print(f"Error al buscar usuarios. Tipo de error: {e}")
        return []
    finally:
        if conexion:
            conexion.close()

def obtener_roles_disponibles():
    """Retorna los roles disponibles en el sistema"""
    return ['admin', 'vendedor', 'inventario', 'reportes']