import React, { useState, useEffect } from 'react';
import { productsApi, cartApi } from '../../services/api';

const ProductDetail = ({ productId }) => {
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const user = JSON.parse(localStorage.getItem('user') || 'null');

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await productsApi.getProduct(productId);
        setProduct(response.producto || null);
      } catch (err) {
        setError('Error al cargar el producto. Por favor, intenta de nuevo más tarde.');
        console.error('Error fetching product:', err);
      } finally {
        setLoading(false);
      }
    };

    if (productId) {
      fetchProduct();
    }
  }, [productId]);

  const handleQuantityChange = (e) => {
    const value = parseInt(e.target.value);
    if (value > 0 && value <= (product?.stock || 99)) {
      setQuantity(value);
    }
  };

  const handleAddToCart = async () => {
    if (!user) {
      window.location.href = '/login';
      return;
    }

    try {
      await cartApi.addToCart(user.id, productId, quantity);
      
      // Dispatch event to update cart counter in navbar
      window.dispatchEvent(new Event('cartUpdated'));
      
      alert('Producto agregado al carrito');
    } catch (err) {
      console.error('Error adding to cart:', err);
      alert('Error al agregar al carrito. Por favor, intenta de nuevo.');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <p className="text-gray-500">Cargando información del producto...</p>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <p className="text-red-500">{error || 'Producto no encontrado'}</p>
        <a href="/products" className="inline-block mt-4 text-gray-600 hover:text-gray-800">
          Volver a productos
        </a>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-4">
        <a href="/products" className="text-gray-600 hover:text-gray-800">
          &larr; Volver a productos
        </a>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="md:flex">
          <div className="md:w-1/2">
            <img
              src={product.url_imagen || 'https://via.placeholder.com/500x500?text=No+Image'}
              alt={product.nombre}
              className="w-full h-auto object-cover"
            />
          </div>
          <div className="md:w-1/2 p-6">
            <div className="mb-2 text-sm text-gray-500">{product.categoria_nombre}</div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">{product.nombre}</h1>
            <div className="text-sm text-gray-600 mb-4">Código: {product.codigo}</div>

            <div className="mb-6">
              {product.precio_descuento ? (
                <div>
                  <span className="text-2xl font-bold text-gray-800">${product.precio_descuento}</span>
                  <span className="text-lg text-gray-500 line-through ml-2">${product.precio}</span>
                </div>
              ) : (
                <span className="text-2xl font-bold text-gray-800">${product.precio}</span>
              )}
            </div>

            <div className="border-t border-b py-4 my-6">
              <div className="mb-4">
                <p className="text-gray-700">{product.descripcion}</p>
              </div>
              
              <div className="flex items-center mb-4">
                <span className="text-gray-700 mr-2">Disponibilidad:</span>
                {product.stock > 0 ? (
                  <span className="text-green-600">En stock ({product.stock} disponibles)</span>
                ) : (
                  <span className="text-red-600">Agotado</span>
                )}
              </div>
              
              {product.requiere_receta === 1 && (
                <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-md mb-4">
                  <p className="text-yellow-700 text-sm">
                    Este producto requiere receta médica para su venta.
                  </p>
                </div>
              )}
            </div>

            <div className="flex items-center mb-6">
              <div className="mr-4">
                <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
                  Cantidad
                </label>
                <input
                  type="number"
                  id="quantity"
                  min="1"
                  max={product.stock}
                  value={quantity}
                  onChange={handleQuantityChange}
                  className="w-16 p-2 border border-gray-300 rounded-md"
                  disabled={product.stock === 0}
                />
              </div>
              
              <button
                onClick={handleAddToCart}
                disabled={product.stock === 0}
                className={`flex-1 p-3 rounded-md ${
                  product.stock === 0 
                    ? 'bg-gray-300 cursor-not-allowed' 
                    : 'bg-gray-700 text-white hover:bg-gray-600'
                }`}
              >
                {product.stock === 0 ? 'Agotado' : 'Agregar al carrito'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;