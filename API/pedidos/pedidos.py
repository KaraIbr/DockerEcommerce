from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
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

# 1. Obtener carrito del usuario
@app.route('/carrito/<int:usuario_id>', methods=['GET'])
def obtener_carrito(usuario_id):
    try:
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Obtener los productos en el carrito con información detallada
        cursor.execute("""
            SELECT c.id, c.usuario_id, c.producto_id, c.cantidad, 
                   p.nombre, p.codigo, p.precio, p.precio_descuento, p.url_imagen,
                   IF(p.precio_descuento IS NOT NULL AND p.precio_descuento > 0, 
                      p.precio_descuento, p.precio) as precio_final
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.usuario_id = %s
        """, (usuario_id,))
        
        items = cursor.fetchall()
        
        # Calcular totales
        subtotal = 0
        total_items = 0
        
        for item in items:
            precio_final = float(item['precio_final'])
            cantidad = item['cantidad']
            item['subtotal'] = precio_final * cantidad
            subtotal += item['subtotal']
            total_items += cantidad
            
            # Convertir decimales a cadena para serialización JSON
            item['precio'] = str(item['precio'])
            if item['precio_descuento']:
                item['precio_descuento'] = str(item['precio_descuento'])
            item['precio_final'] = str(item['precio_final'])
            item['subtotal'] = str(item['subtotal'])
        
        # Calcular impuestos y total
        impuesto = round(subtotal * 0.16, 2)  # IVA del 16%
        envio = 0  # Puedes implementar lógica para costos de envío si lo deseas
        total = subtotal + impuesto + envio
        
        # Preparar la respuesta
        respuesta = {
            'items': items,
            'resumen': {
                'subtotal': str(subtotal),
                'impuesto': str(impuesto),
                'envio': str(envio),
                'total': str(total),
                'total_items': total_items
            }
        }
        
        cursor.close()
        conn.close()
        
        return jsonify(respuesta), 200
    except Exception as e:
        print(f"Error obteniendo carrito: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 2. Agregar producto al carrito
@app.route('/carrito', methods=['POST'])
def agregar_al_carrito():
    try:
        datos = request.json
        usuario_id = datos.get('usuario_id')
        
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si el producto ya está en el carrito
        cursor.execute(
            "SELECT id, cantidad FROM carrito WHERE usuario_id = %s AND producto_id = %s",
            (usuario_id, datos.get('producto_id'))
        )
        item_existente = cursor.fetchone()
        
        if item_existente:
            # Actualizar cantidad
            nueva_cantidad = item_existente['cantidad'] + datos.get('cantidad', 1)
            cursor.execute(
                "UPDATE carrito SET cantidad = %s WHERE id = %s",
                (nueva_cantidad, item_existente['id'])
            )
            conn.commit()
            mensaje = 'Cantidad actualizada en el carrito'
            item_id = item_existente['id']
        else:
            # Agregar producto nuevo al carrito
            cursor.execute(
                "INSERT INTO carrito (usuario_id, producto_id, cantidad) VALUES (%s, %s, %s)",
                (usuario_id, datos.get('producto_id'), datos.get('cantidad', 1))
            )
            conn.commit()
            mensaje = 'Producto agregado al carrito'
            item_id = cursor.lastrowid
        
        # Obtener información actualizada del carrito
        cursor.execute("""
            SELECT c.id, c.usuario_id, c.producto_id, c.cantidad, 
                   p.nombre, p.codigo, p.precio, p.precio_descuento, p.url_imagen
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.id = %s
        """, (item_id,))
        
        item = cursor.fetchone()
        
        if item:
            if 'precio' in item:
                item['precio'] = str(item['precio'])
            if item['precio_descuento']:
                item['precio_descuento'] = str(item['precio_descuento'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'mensaje': mensaje,
            'item': item
        }), 200
    except Exception as e:
        print(f"Error agregando al carrito: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 3. Actualizar cantidad de un producto en el carrito
@app.route('/carrito/<int:item_id>', methods=['PUT'])
def actualizar_carrito(item_id):
    try:
        datos = request.json
        cantidad = datos.get('cantidad', 1)
        
        if cantidad <= 0:
            return jsonify({'mensaje': 'La cantidad debe ser mayor a cero'}), 400
            
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si el item existe
        cursor.execute("SELECT usuario_id FROM carrito WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'mensaje': 'Item no encontrado'}), 404
        
        # Actualizar cantidad
        cursor.execute("UPDATE carrito SET cantidad = %s WHERE id = %s", (cantidad, item_id))
        conn.commit()
        
        # Obtener item actualizado
        cursor.execute("""
            SELECT c.id, c.usuario_id, c.producto_id, c.cantidad, 
                   p.nombre, p.codigo, p.precio, p.precio_descuento, p.url_imagen
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.id = %s
        """, (item_id,))
        
        item_actualizado = cursor.fetchone()
        
        if item_actualizado:
            if 'precio' in item_actualizado:
                item_actualizado['precio'] = str(item_actualizado['precio'])
            if item_actualizado['precio_descuento']:
                item_actualizado['precio_descuento'] = str(item_actualizado['precio_descuento'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'mensaje': 'Cantidad actualizada',
            'item': item_actualizado
        }), 200
    except Exception as e:
        print(f"Error actualizando carrito: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 4. Eliminar producto del carrito
@app.route('/carrito/<int:item_id>', methods=['DELETE'])
def eliminar_del_carrito(item_id):
    try:
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si el item existe
        cursor.execute("SELECT usuario_id FROM carrito WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'mensaje': 'Item no encontrado'}), 404
            
        # Eliminar item
        cursor.execute("DELETE FROM carrito WHERE id = %s", (item_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'mensaje': 'Producto eliminado del carrito'}), 200
    except Exception as e:
        print(f"Error eliminando del carrito: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 5. Procesar el checkout
@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        datos = request.json
        usuario_id = datos.get('usuario_id')
        
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si hay productos en el carrito
        cursor.execute("""
            SELECT c.id, c.producto_id, c.cantidad, 
                   p.nombre, p.precio, p.precio_descuento, p.stock,
                   IF(p.precio_descuento IS NOT NULL AND p.precio_descuento > 0, 
                      p.precio_descuento, p.precio) as precio_final
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.usuario_id = %s
        """, (usuario_id,))
        
        items = cursor.fetchall()
        
        if not items:
            return jsonify({'mensaje': 'No hay productos en el carrito'}), 400
        
        # Calcular totales
        subtotal = 0
        detalles = []
        
        for item in items:
            precio_final = float(item['precio_final'])
            cantidad = item['cantidad']
            subtotal += precio_final * cantidad
            
            # Verificar stock
            if item['stock'] < cantidad:
                return jsonify({
                    'mensaje': f"Stock insuficiente para {item['nombre']}. Disponible: {item['stock']}"
                }), 400
                
            detalles.append({
                'producto_id': item['producto_id'],
                'cantidad': cantidad,
                'precio_unitario': precio_final
            })
        
        # Calcular impuestos y total
        impuesto = round(subtotal * 0.16, 2)  # IVA del 16%
        envio = 0  # Puedes implementar lógica para costos de envío
        total = subtotal + impuesto + envio
        
        # Crear pedido
        direccion_entrega = datos.get('direccion_entrega', '')
        metodo_pago = datos.get('metodo_pago', 'efectivo')
        
        cursor.execute("""
            INSERT INTO pedidos 
            (usuario_id, subtotal, impuesto, costo_envio, total, estado, direccion_entrega, metodo_pago, fecha_creacion) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            usuario_id, 
            subtotal, 
            impuesto, 
            envio, 
            total, 
            'pendiente', 
            direccion_entrega, 
            metodo_pago,
            datetime.datetime.now()
        ))
        
        pedido_id = cursor.lastrowid
        
        # Crear detalles del pedido
        for detalle in detalles:
            cursor.execute("""
                INSERT INTO detalles_pedido 
                (pedido_id, producto_id, cantidad, precio_unitario) 
                VALUES (%s, %s, %s, %s)
            """, (
                pedido_id,
                detalle['producto_id'],
                detalle['cantidad'],
                detalle['precio_unitario']
            ))
            
            # Actualizar stock
            cursor.execute("""
                UPDATE productos 
                SET stock = stock - %s 
                WHERE id = %s
            """, (
                detalle['cantidad'],
                detalle['producto_id']
            ))
        
        # Eliminar productos del carrito
        cursor.execute("DELETE FROM carrito WHERE usuario_id = %s", (usuario_id,))
        
        conn.commit()
        
        # Obtener el pedido creado
        cursor.execute("""
            SELECT id, usuario_id, subtotal, impuesto, costo_envio, total, 
                   estado, direccion_entrega, metodo_pago, fecha_creacion 
            FROM pedidos 
            WHERE id = %s
        """, (pedido_id,))
        
        pedido = cursor.fetchone()
        
        if pedido:
            # Convertir decimales a cadena para serialización JSON
            pedido['subtotal'] = str(pedido['subtotal'])
            pedido['impuesto'] = str(pedido['impuesto'])
            pedido['costo_envio'] = str(pedido['costo_envio'])
            pedido['total'] = str(pedido['total'])
            
            # Formatear la fecha
            if 'fecha_creacion' in pedido and pedido['fecha_creacion']:
                pedido['fecha_creacion'] = pedido['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'mensaje': 'Pedido procesado correctamente',
            'pedido': pedido
        }), 201
    except Exception as e:
        print(f"Error en checkout: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 6. Obtener historial de pedidos de un usuario
@app.route('/pedidos/usuario/<int:usuario_id>', methods=['GET'])
def obtener_pedidos_usuario(usuario_id):
    try:
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Obtener pedidos
        cursor.execute("""
            SELECT id, usuario_id, subtotal, impuesto, costo_envio, total, 
                   estado, direccion_entrega, metodo_pago, fecha_creacion 
            FROM pedidos 
            WHERE usuario_id = %s
            ORDER BY fecha_creacion DESC
        """, (usuario_id,))
        
        pedidos = cursor.fetchall()
        
        # Procesar cada pedido
        for pedido in pedidos:
            # Convertir decimales a cadena para serialización JSON
            pedido['subtotal'] = str(pedido['subtotal'])
            pedido['impuesto'] = str(pedido['impuesto'])
            pedido['costo_envio'] = str(pedido['costo_envio'])
            pedido['total'] = str(pedido['total'])
            
            # Formatear la fecha
            if 'fecha_creacion' in pedido and pedido['fecha_creacion']:
                pedido['fecha_creacion'] = pedido['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Obtener detalles de cada pedido
            cursor.execute("""
                SELECT dp.*, p.nombre, p.codigo, p.url_imagen
                FROM detalles_pedido dp
                JOIN productos p ON dp.producto_id = p.id
                WHERE dp.pedido_id = %s
            """, (pedido['id'],))
            
            detalles = cursor.fetchall()
            
            for detalle in detalles:
                if 'precio_unitario' in detalle:
                    detalle['precio_unitario'] = str(detalle['precio_unitario'])
                if 'subtotal' in detalle:
                    detalle['subtotal'] = str(detalle['subtotal'])
            
            pedido['detalles'] = detalles
        
        cursor.close()
        conn.close()
        
        return jsonify({'pedidos': pedidos}), 200
    except Exception as e:
        print(f"Error obteniendo pedidos: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)