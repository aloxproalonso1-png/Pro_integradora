from database import crear_conexion

def obtener_productos():
    """Obtiene todos los productos"""
    conexion = crear_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_producto, nombre_producto, stock, precio, proveedor FROM productos")
        resultado = cursor.fetchall()
        return resultado
    except Exception as e:
        print(f"Error al obtener productos. Tipo de error: {e}")
        return []
    finally:
        if conexion:
            conexion.close()

def obtener_producto_por_id(id_producto):
    """Obtiene un producto específico por ID"""
    conexion = crear_conexion()
    if not conexion:
        return None
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_producto, nombre_producto, stock, precio, proveedor FROM productos WHERE id_producto = %s", (id_producto,))
        resultado = cursor.fetchone()
        return resultado
    except Exception as e:
        print(f"Error al obtener producto por ID. Tipo de error: {e}")
        return None
    finally:
        if conexion:
            conexion.close()

def obtener_productos_stock_bajo(limite=5):
    """Obtiene productos con stock bajo"""
    conexion = crear_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_producto, nombre_producto, stock, precio, proveedor FROM productos WHERE stock <= %s", (limite,))
        resultado = cursor.fetchall()
        return resultado
    except Exception as e:
        print(f"Error al obtener productos con stock bajo. Tipo de error: {e}")
        return []
    finally:
        if conexion:
            conexion.close()

def agregar_producto(nombre_producto, stock, precio, proveedor):
    """Agrega un nuevo producto"""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO productos (nombre_producto, stock, precio, proveedor) VALUES (%s, %s, %s, %s)", 
                      (nombre_producto, stock, precio, proveedor))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al agregar producto. Tipo de error: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def actualizar_producto(id_producto, nuevo_nombre, nuevo_stock, nuevo_precio, nuevo_proveedor):
    """Actualiza un producto existente"""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE productos SET nombre_producto = %s, stock = %s, precio = %s, proveedor = %s WHERE id_producto = %s", 
                      (nuevo_nombre, nuevo_stock, nuevo_precio, nuevo_proveedor, id_producto))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar producto. Tipo de error: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def actualizar_stock(id_producto, nuevo_stock):
    """Actualiza solo el stock de un producto"""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", 
                      (nuevo_stock, id_producto))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar stock. Tipo de error: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def incrementar_stock(id_producto, cantidad):
    """Incrementa el stock de un producto"""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE productos SET stock = stock + %s WHERE id_producto = %s", 
                      (cantidad, id_producto))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al incrementar stock. Tipo de error: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def disminuir_stock(id_producto, cantidad):
    """Disminuye el stock de un producto"""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        # Verificar que haya stock suficiente
        producto = obtener_producto_por_id(id_producto)
        if producto and producto['stock'] >= cantidad:
            cursor = conexion.cursor()
            cursor.execute("UPDATE productos SET stock = stock - %s WHERE id_producto = %s", 
                          (cantidad, id_producto))
            conexion.commit()
            return True
        else:
            print("Stock insuficiente")
            return False
    except Exception as e:
        print(f"Error al disminuir stock. Tipo de error: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def eliminar_producto(id_producto):
    """Elimina un producto"""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar producto. Tipo de error: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def buscar_productos(termino_busqueda):
    """Busca productos por nombre o proveedor"""
    conexion = crear_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_producto, nombre_producto, stock, precio, proveedor FROM productos WHERE nombre_producto LIKE %s OR proveedor LIKE %s", 
                      (f"%{termino_busqueda}%", f"%{termino_busqueda}%"))
        resultado = cursor.fetchall()
        return resultado
    except Exception as e:
        print(f"Error al buscar productos. Tipo de error: {e}")
        return []
    finally:
        if conexion:
            conexion.close()