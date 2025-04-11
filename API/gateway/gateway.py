from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000", 
            "http://127.0.0.1:3000",
            "http://localhost:5501",
            "http://127.0.0.1:5501"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

USUARIOS_URL = os.getenv('USUARIOS_URL', 'http://usuarios:5001')
CATALOGO_URL = os.getenv('CATALOGO_URL', 'http://catalogo:5002')
PEDIDOS_URL = os.getenv('PEDIDOS_URL', 'http://pedidos:5003')

# 1. Autenticación
@app.route('/auth/login', methods=['POST'])
def login():
    response = requests.post(f"{USUARIOS_URL}/login", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/auth/registro', methods=['POST'])
def registro():
    response = requests.post(f"{USUARIOS_URL}/registro", json=request.json)
    return jsonify(response.json()), response.status_code

# 2. Usuarios
@app.route('/usuarios/perfil', methods=['GET'])
def obtener_perfil():
    usuario_id = request.args.get('usuario_id')
    if not usuario_id:
        return jsonify({'mensaje': 'ID de usuario requerido'}), 400
    
    response = requests.get(f"{USUARIOS_URL}/perfil/{usuario_id}")
    return jsonify(response.json()), response.status_code

@app.route('/usuarios/perfil', methods=['PUT'])
def actualizar_perfil():
    usuario_id = request.args.get('usuario_id')
    if not usuario_id:
        return jsonify({'mensaje': 'ID de usuario requerido'}), 400
    
    response = requests.put(f"{USUARIOS_URL}/perfil/{usuario_id}", json=request.json)
    return jsonify(response.json()), response.status_code

# 3. Catálogo
@app.route('/productos', methods=['GET'])
def obtener_productos():
    response = requests.get(f"{CATALOGO_URL}/productos", params=request.args.to_dict())
    return jsonify(response.json()), response.status_code

@app.route('/productos/<int:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    response = requests.get(f"{CATALOGO_URL}/productos/{producto_id}")
    return jsonify(response.json()), response.status_code

@app.route('/categorias', methods=['GET'])
def obtener_categorias():
    response = requests.get(f"{CATALOGO_URL}/categorias")
    return jsonify(response.json()), response.status_code

# 4. Admin productos
@app.route('/productos', methods=['POST'])
def crear_producto():
    response = requests.post(f"{CATALOGO_URL}/productos", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/productos/<int:producto_id>', methods=['PUT'])
def actualizar_producto(producto_id):
    response = requests.put(f"{CATALOGO_URL}/productos/{producto_id}", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/productos/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    response = requests.delete(f"{CATALOGO_URL}/productos/{producto_id}")
    return jsonify(response.json()), response.status_code

# 5. Carrito y pedidos
@app.route('/carrito', methods=['GET'])
def obtener_carrito():
    usuario_id = request.args.get('usuario_id')
    if not usuario_id:
        return jsonify({'mensaje': 'ID de usuario requerido'}), 400
        
    response = requests.get(f"{PEDIDOS_URL}/carrito/{usuario_id}")
    return jsonify(response.json()), response.status_code

@app.route('/carrito', methods=['POST'])
def agregar_al_carrito():
    response = requests.post(f"{PEDIDOS_URL}/carrito", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/carrito/actualizar/<int:item_id>', methods=['PUT'])
def actualizar_carrito(item_id):
    response = requests.put(f"{PEDIDOS_URL}/carrito/{item_id}", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/carrito/eliminar/<int:item_id>', methods=['DELETE'])
def eliminar_del_carrito(item_id):
    response = requests.delete(f"{PEDIDOS_URL}/carrito/{item_id}")
    return jsonify(response.json()), response.status_code

@app.route('/checkout', methods=['POST'])
def checkout():
    response = requests.post(f"{PEDIDOS_URL}/checkout", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/pedidos', methods=['GET'])
def obtener_pedidos():
    usuario_id = request.args.get('usuario_id')
    if not usuario_id:
        return jsonify({'mensaje': 'ID de usuario requerido'}), 400
        
    response = requests.get(f"{PEDIDOS_URL}/pedidos/usuario/{usuario_id}")
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)