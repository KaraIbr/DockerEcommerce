from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'luna')
}

def obtener_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        return None

# 1. Login
@app.route('/login', methods=['POST'])
def login():
    try:
        datos = request.json
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (datos.get('email'),))
        usuario = cursor.fetchone()
        
        if not usuario or not bcrypt.checkpw(datos.get('password', '').encode(), usuario['password'].encode()):
            return jsonify({'mensaje': 'Credenciales incorrectas'}), 401
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'usuario': {
                'id': usuario['id'],
                'nombre': usuario['nombre'],
                'email': usuario['correo'],
                'rol': usuario['rol']
            }
        }), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error en login: {str(e)}'}), 500

# 2. Registro
@app.route('/registro', methods=['POST'])
def registro():
    try:
        datos = request.json
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (datos.get('email'),))
        if cursor.fetchone():
            return jsonify({'mensaje': 'Email ya registrado'}), 409
        
        hashed = bcrypt.hashpw(datos.get('password', '').encode(), bcrypt.gensalt())
        
        cursor.execute(
            "INSERT INTO usuarios (correo, password, nombre, telefono, direccion, rol) VALUES (%s, %s, %s, %s, %s, %s)",
            (datos.get('email'), 
             hashed.decode(), 
             datos.get('nombre'), 
             datos.get('telefono', ''), 
             datos.get('direccion', ''),
             'cliente')
        )
        conn.commit()
        
        usuario_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            'mensaje': 'Registro exitoso',
            'usuario': {
                'id': usuario_id,
                'nombre': datos.get('nombre'),
                'email': datos.get('email'),
                'rol': 'cliente'
            }
        }), 201
    except Exception as e:
        return jsonify({'mensaje': f'Error en registro: {str(e)}'}), 500

# 3. Obtener perfil
@app.route('/perfil/<int:usuario_id>', methods=['GET'])
def obtener_perfil(usuario_id):
    try:
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, correo, nombre, telefono, rol, direccion FROM usuarios WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not usuario:
            return jsonify({'mensaje': 'Usuario no encontrado'}), 404
            
        return jsonify({'usuario': usuario}), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error al obtener perfil: {str(e)}'}), 500

# 4. Actualizar perfil
@app.route('/perfil/<int:usuario_id>', methods=['PUT'])
def actualizar_perfil(usuario_id):
    try:
        datos = request.json
        conn = obtener_db()
        if not conn:
            return jsonify({'mensaje': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor()
        
        campos = []
        valores = []
        
        if 'nombre' in datos:
            campos.append("nombre = %s")
            valores.append(datos['nombre'])
        
        if 'telefono' in datos:
            campos.append("telefono = %s")
            valores.append(datos['telefono'])
        
        if 'direccion' in datos:
            campos.append("direccion = %s")
            valores.append(datos['direccion'])
        
        if not campos:
            return jsonify({'mensaje': 'No hay datos para actualizar'}), 400
        
        valores.append(usuario_id)
        query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = %s"
        
        cursor.execute(query, valores)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'mensaje': 'Perfil actualizado'}), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error al actualizar perfil: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)