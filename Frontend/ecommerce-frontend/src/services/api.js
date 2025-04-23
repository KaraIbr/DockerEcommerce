import axios from 'axios';

// Configuración del cliente axios
const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// API de productos
export const productsApi = {
  // Obtener todos los productos con opciones de filtrado
  getProducts: async (filters = {}) => {
    try {
      const response = await api.get('/productos', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  // Obtener un producto por ID
  getProduct: async (productId) => {
    try {
      const response = await api.get(`/productos/${productId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching product ${productId}:`, error);
      throw error;
    }
  },

  // Obtener todas las categorías
  getCategories: async () => {
    try {
      const response = await api.get('/categorias');
      return response.data;
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  }
};

// API del carrito
export const cartApi = {
  // Obtener el carrito del usuario
  getCart: async (userId) => {
    try {
      const response = await api.get(`/carrito?usuario_id=${userId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching cart for user ${userId}:`, error);
      throw error;
    }
  },

  // Agregar producto al carrito
  addToCart: async (userId, productId, quantity = 1) => {
    try {
      const response = await api.post('/carrito', {
        usuario_id: userId,
        producto_id: productId,
        cantidad: quantity
      });
      return response.data;
    } catch (error) {
      console.error('Error adding product to cart:', error);
      throw error;
    }
  },

  // Actualizar cantidad de un producto en el carrito
  updateCartItem: async (itemId, quantity) => {
    try {
      const response = await api.put(`/carrito/actualizar/${itemId}`, {
        cantidad: quantity
      });
      return response.data;
    } catch (error) {
      console.error(`Error updating cart item ${itemId}:`, error);
      throw error;
    }
  },

  // Eliminar producto del carrito
  removeFromCart: async (itemId) => {
    try {
      const response = await api.delete(`/carrito/eliminar/${itemId}`);
      return response.data;
    } catch (error) {
      console.error(`Error removing item ${itemId} from cart:`, error);
      throw error;
    }
  }
};

// API de pedidos
export const ordersApi = {
  // Procesar checkout
  checkout: async (userId, shippingInfo) => {
    try {
      const response = await api.post('/checkout', {
        usuario_id: userId,
        direccion_entrega: shippingInfo.address,
        metodo_pago: shippingInfo.paymentMethod || 'efectivo'
      });
      return response.data;
    } catch (error) {
      console.error('Error processing checkout:', error);
      throw error;
    }
  },

  // Obtener historial de pedidos
  getOrders: async (userId) => {
    try {
      const response = await api.get(`/pedidos?usuario_id=${userId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching orders for user ${userId}:`, error);
      throw error;
    }
  }
};

// API de usuarios
export const userApi = {
  // Obtener perfil de usuario
  getProfile: async (userId) => {
    try {
      const response = await api.get(`/usuarios/perfil?usuario_id=${userId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching profile for user ${userId}:`, error);
      throw error;
    }
  },

  // Actualizar perfil de usuario
  updateProfile: async (userId, profileData) => {
    try {
      const response = await api.put(`/usuarios/perfil?usuario_id=${userId}`, profileData);
      return response.data;
    } catch (error) {
      console.error(`Error updating profile for user ${userId}:`, error);
      throw error;
    }
  }
};

// API de autenticación
export const authApi = {
  // Iniciar sesión
  login: async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      return response.data;
    } catch (error) {
      console.error('Error during login:', error);
      throw error;
    }
  },

  // Registrarse
  register: async (userData) => {
    try {
      const response = await api.post('/auth/registro', userData);
      return response.data;
    } catch (error) {
      console.error('Error during registration:', error);
      throw error;
    }
  }
};

export default {
  productsApi,
  cartApi,
  ordersApi,
  userApi,
  authApi
};