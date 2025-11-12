from database import crear_conexion

def ver_producto():
    conexion = crear_conexion()
    if not conexion:
        return []
    
    cursor = conexion.cursor()
    cursor.execute("SELECT id_producto, nombre_producto, stock, precio, proveedor FROM productos")
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def agregar_productos(nombre_producto, stock, precio, proveedor):
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        # CORREGIDO: El orden correcto es nombre, stock, precio, proveedor
        cursor.execute("INSERT INTO productos (nombre_producto, stock, precio, proveedor) VALUES (%s, %s, %s, %s)", 
                      (nombre_producto, stock, precio, proveedor))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al agregar un producto. Tipo de error {e}")
        return False

def actualizar_productos(id_producto, new_nombre_producto, new_stock, new_precio, new_proveedor):
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        # CORREGIDO: Agregar WHERE y orden correcto
        cursor.execute("UPDATE productos SET nombre_producto = %s, stock = %s, precio = %s, proveedor = %s WHERE id_producto = %s", 
                      (new_nombre_producto, new_stock, new_precio, new_proveedor, id_producto))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al actualizar productos. Tipo de error: {e}")
        return False

def eliminar_producto(id_producto):
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al eliminar producto. Tipo de error: {e}")
        return False