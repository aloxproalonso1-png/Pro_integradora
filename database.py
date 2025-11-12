import mysql.connector
from mysql.connector import Error

def crear_conexion():
    try:
        conexion=mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",
            database = "barberia_bravo"
        )

        if conexion.is_connected():
            print("conexion mysql exitosa")
            return conexion
        
    except Error as e:
        print(f"En este momento no posible comunicarse con el sistema, intentelo mas tarde ...{e}")
        return None    