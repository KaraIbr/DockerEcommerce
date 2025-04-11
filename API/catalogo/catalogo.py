from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
# Permitir que react/js pueda hacer peticiones a la API
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://127.0.0.1:5501",
            "http://localhost:5501",
            "http://localhost:3000", 
            "http://127.0.0.1:3000"  
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'luna2025'),
    'database': os.getenv('DB_NAME', 'luna')
}

def obtener_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        return None

# 1. Obtener todos los productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    try:
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        busqueda = request.args.get('busqueda', '')
        categoria_id = request.args.get('categoria_id')
        
        query = "SELECT p.*, c.nombre as categoria_nombre FROM productos p JOIN categorias c ON p.categoria_id = c.id WHERE 1=1"
        params = []
        
        if busqueda:
            query += " AND (p.nombre LIKE %s OR p.codigo LIKE %s)"
            term = f"%{busqueda}%"
            params.extend([term, term])
            
        if categoria_id:
            query += " AND p.categoria_id = %s"
            params.append(int(categoria_id))
        
        query += " ORDER BY p.id DESC"
        
        cursor.execute(query, params)
        productos = cursor.fetchall()
        
        for p in productos:
            if 'precio' in p:
                p['precio'] = str(p['precio'])
            if p['precio_descuento']:
                p['precio_descuento'] = str(p['precio_descuento'])
        
        cursor.close()
        conn.close()
        
        return jsonify({'productos': productos}), 200
    except Exception as e:
        print(f"Error obteniendo productos: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 2. Obtener un producto
@app.route('/productos/<int:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    try:
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT p.*, c.nombre as categoria_nombre FROM productos p JOIN categorias c ON p.categoria_id = c.id WHERE p.id = %s",
            (producto_id,)
        )
        producto = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404
        
        if 'precio' in producto:
            producto['precio'] = str(producto['precio'])
        if producto['precio_descuento']:
            producto['precio_descuento'] = str(producto['precio_descuento'])
        
        return jsonify({'producto': producto}), 200
    except Exception as e:
        print(f"Error obteniendo producto {producto_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 3. Crear producto (admin)
@app.route('/productos', methods=['POST'])
def crear_producto():
    try:
        datos = request.json
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO productos 
               (codigo, nombre, descripcion, precio, precio_descuento, stock, categoria_id, requiere_receta, url_imagen) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                datos.get('codigo'), 
                datos.get('nombre'), 
                datos.get('descripcion', ''),
                datos.get('precio'), 
                datos.get('precio_descuento'),
                datos.get('stock', 0),
                datos.get('categoria_id'),
                datos.get('requiere_receta', 0),
                datos.get('url_imagen')
            )
        )
        conn.commit()
        producto_id = cursor.lastrowid
        
        # Obtener el producto recién creado
        cursor.execute(
            "SELECT p.*, c.nombre as categoria_nombre FROM productos p JOIN categorias c ON p.categoria_id = c.id WHERE p.id = %s",
            (producto_id,)
        )
        producto = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({'mensaje': 'Producto creado', 'producto': producto}), 201
    except Exception as e:
        print(f"Error al crear producto: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 4. Actualizar producto (admin)
@app.route('/productos/<int:producto_id>', methods=['PUT'])
def actualizar_producto(producto_id):
    try:
        datos = request.json
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor()
        
        campos = []
        valores = []
        
        for campo in ['codigo', 'nombre', 'descripcion', 'precio', 'precio_descuento', 'stock', 'categoria_id', 'requiere_receta', 'url_imagen']:
            if campo in datos:
                campos.append(f"{campo} = %s")
                valores.append(datos[campo])
        
        if not campos:
            return jsonify({"error": "No hay datos para actualizar"}), 400
        
        valores.append(producto_id)
        query = f"UPDATE productos SET {', '.join(campos)} WHERE id = %s"
        
        cursor.execute(query, valores)
        conn.commit()
        
        # Obtener el producto actualizado
        cursor.execute(
            "SELECT p.*, c.nombre as categoria_nombre FROM productos p JOIN categorias c ON p.categoria_id = c.id WHERE p.id = %s",
            (producto_id,)
        )
        producto = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({'mensaje': 'Producto actualizado', 'producto': producto}), 200
    except Exception as e:
        print(f"Error actualizando producto {producto_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 5. Eliminar producto (admin)
@app.route('/productos/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    try:
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'mensaje': 'Producto eliminado'}), 200
    except Exception as e:
        print(f"Error eliminando producto {producto_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 6. Obtener categorías
@app.route('/categorias', methods=['GET'])
def obtener_categorias():
    try:
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM categorias")
        categorias = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'categorias': categorias}), 200
    except Exception as e:
        print(f"Error obteniendo categorías: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 7. Obtener productos de una categoría
@app.route('/categorias/<int:categoria_id>/productos', methods=['GET'])
def obtener_productos_categoria(categoria_id):
    try:
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT p.*, c.nombre as categoria_nombre FROM productos p JOIN categorias c ON p.categoria_id = c.id WHERE p.categoria_id = %s",
            (categoria_id,)
        )
        productos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        for p in productos:
            if 'precio' in p:
                p['precio'] = str(p['precio'])
            if p['precio_descuento']:
                p['precio_descuento'] = str(p['precio_descuento'])
        
        return jsonify({'productos': productos}), 200
    except Exception as e:
        print(f"Error obteniendo productos por categoría: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)