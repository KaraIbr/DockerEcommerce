import React, { useState, useEffect } from 'react';
import { cartApi, ordersApi } from '../../services/api';

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [summary, setSummary] = useState({
    subtotal: '0',
    impuesto: '0',
    envio: '0',
    total: '0',
    total_items: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  
  const user = JSON.parse(localStorage.getItem('user') || 'null');

  useEffect(() => {
    if (!user) {
      window.location.href = '/login';
      return;
    }
    
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await cartApi.getCart(user.id);
      setCartItems(response.items || []);
      setSummary(response.resumen || {
        subtotal: '0',
        impuesto: '0',
        envio: '0',
        total: '0',
        total_items: 0
      });
    } catch (err) {
      setError('Error al cargar el carrito. Por favor, intenta de nuevo más tarde.');
      console.error('Error fetching cart:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateQuantity = async (itemId, newQuantity) => {
    if (newQuantity < 1) return;
    
    try {
      await cartApi.updateCartItem(itemId, newQuantity);
      
      // Update local state to avoid a full refresh
      const updatedItems = cartItems.map(item => 
        item.id === itemId ? { ...item, cantidad: newQuantity } : item
      );
      setCartItems(updatedItems);
      
      // Refresh cart to update totals
      fetchCart();
      
      // Dispatch event to update cart counter in navbar
      window.dispatchEvent(new Event('cartUpdated'));
    } catch (err) {
      console.error('Error updating cart item quantity:', err);
      alert('Error al actualizar la cantidad. Por favor, intenta de nuevo.');
    }
  };

  const handleRemoveItem = async (itemId) => {
    try {
      await cartApi.removeFromCart(itemId);
      
      // Update local state to remove the item
      const updatedItems = cartItems.filter(item => item.id !== itemId);
      setCartItems(updatedItems);
      
      // Refresh cart to update totals
      fetchCart();
      
      // Dispatch event to update cart counter in navbar
      window.dispatchEvent(new Event('cartUpdated'));
    } catch (err) {
      console.error('Error removing cart item:', err);
      alert('Error al eliminar el producto. Por favor, intenta de nuevo.');
    }
  };

  const handleCheckout = async () => {
    if (cartItems.length === 0) {
      alert('Tu carrito está vacío');
      return;
    }
    
    try {
      setCheckoutLoading(true);
      
      // Simple checkout with minimal shipping info
      const shippingInfo = {
        address: user.direccion || '',
        city: '',
        zipCode: '',
        paymentMethod: 'efectivo'
      };
      
      const response = await ordersApi.checkout(user.id, shippingInfo);
      
      // Refresh cart (should be empty now)
      fetchCart();
      
      // Update cart counter in navbar
      window.dispatchEvent(new Event('cartUpdated'));
      
      // Show success message
      alert(`Pedido procesado correctamente. Número de pedido: ${response.pedido.id}`);
      
      // Redirect to home page
      window.location.href = '/';
    } catch (err) {
      console.error('Error during checkout:', err);
      alert(err.response?.data?.mensaje || 'Error al procesar el pedido. Por favor, intenta de nuevo.');
    } finally {
      setCheckoutLoading(false);
    }
  };

  if (!user) {
    return null; // Avoid flash before redirect
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <p className="text-gray-500">Cargando carrito...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <p className="text-red-500">{error}</p>
        <button 
          onClick={fetchCart}
          className="mt-4 px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300"
        >
          Intentar de nuevo
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Carrito de Compras</h1>
      
      {cartItems.length === 0 ? (
        <div className="bg-white p-8 rounded-lg shadow-sm text-center">
          <p className="text-gray-500 mb-4">Tu carrito está vacío</p>
          <a href="/products" className="inline-block px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600">
            Continuar comprando
          </a>
        </div>
      ) : (
        <div className="lg:flex lg:gap-8">
          {/* Cart items */}
          <div className="lg:w-2/3">
            <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-6">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Producto
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Precio
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cantidad
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Subtotal
                    </th>
                    <th scope="col" className="relative px-6 py-3">
                      <span className="sr-only">Eliminar</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {cartItems.map(item => (
                    <tr key={item.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-16 w-16">
                            <img 
                              className="h-16 w-16 object-cover" 
                              src={item.url_imagen || 'https://via.placeholder.com/150?text=No+Image'} 
                              alt={item.nombre} 
                            />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {item.nombre}
                            </div>
                            <div className="text-sm text-gray-500">
                              Código: {item.codigo}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          ${item.precio_final}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <button
                            onClick={() => handleUpdateQuantity(item.id, Math.max(1, item.cantidad - 1))}
                            className="p-1 rounded-md hover:bg-gray-100"
                          >
                            -
                          </button>
                          <input
                            type="number"
                            min="1"
                            value={item.cantidad}
                            onChange={(e) => handleUpdateQuantity(item.id, parseInt(e.target.value) || 1)}
                            className="mx-2 w-12 p-1 text-center border border-gray-300 rounded-md"
                          />
                          <button
                            onClick={() => handleUpdateQuantity(item.id, item.cantidad + 1)}
                            className="p-1 rounded-md hover:bg-gray-100"
                          >
                            +
                          </button>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          ${item.subtotal}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleRemoveItem(item.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Eliminar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Order summary */}
          <div className="lg:w-1/3">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Resumen del pedido</h2>
              
              <div className="border-t border-gray-200 pt-4 space-y-3">
                <div className="flex justify-between">
                  <p className="text-gray-600">Subtotal</p>
                  <p className="text-gray-800 font-medium">${summary.subtotal}</p>
                </div>
                <div className="flex justify-between">
                  <p className="text-gray-600">Impuestos (16%)</p>
                  <p className="text-gray-800 font-medium">${summary.impuesto}</p>
                </div>
                <div className="flex justify-between">
                  <p className="text-gray-600">Envío</p>
                  <p className="text-gray-800 font-medium">${summary.envio}</p>
                </div>
                
                <div className="border-t border-gray-200 pt-3 mt-3">
                  <div className="flex justify-between">
                    <p className="text-lg font-bold text-gray-900">Total</p>
                    <p className="text-lg font-bold text-gray-900">${summary.total}</p>
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <button
                  onClick={handleCheckout}
                  disabled={checkoutLoading || cartItems.length === 0}
                  className={`w-full py-3 px-4 rounded-md text-white font-medium 
                    ${(checkoutLoading || cartItems.length === 0) 
                      ? 'bg-gray-400 cursor-not-allowed' 
                      : 'bg-gray-700 hover:bg-gray-600'}`}
                >
                  {checkoutLoading ? 'Procesando...' : 'Finalizar compra'}
                </button>
              </div>
              
              <div className="mt-4 text-center">
                <a href="/products" className="text-gray-600 hover:text-gray-800 text-sm">
                  Continuar comprando
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;