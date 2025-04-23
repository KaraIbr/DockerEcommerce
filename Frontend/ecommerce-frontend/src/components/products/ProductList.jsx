import React, { useState, useEffect } from 'react';
import { productsApi, cartApi } from '../../services/api';

const ProductList = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  const user = JSON.parse(localStorage.getItem('user') || 'null');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Build filter object
        const filters = {};
        if (selectedCategory) filters.categoria_id = selectedCategory;
        if (searchTerm) filters.busqueda = searchTerm;
        
        const response = await productsApi.getProducts(filters);
        setProducts(response.productos || []);
      } catch (err) {
        setError('Error al cargar los productos. Por favor, intenta de nuevo más tarde.');
        console.error('Error fetching products:', err);
      } finally {
        setLoading(false);
      }
    };

    const fetchCategories = async () => {
      try {
        const response = await productsApi.getCategories();
        setCategories(response.categorias || []);
      } catch (err) {
        console.error('Error fetching categories:', err);
      }
    };

    fetchProducts();
    fetchCategories();
  }, [selectedCategory, searchTerm]);

  const handleAddToCart = async (productId) => {
    if (!user) {
      window.location.href = '/login';
      return;
    }

    try {
      await cartApi.addToCart(user.id, productId, 1);
      
      // Dispatch event to update cart counter in navbar
      window.dispatchEvent(new Event('cartUpdated'));
      
      alert('Producto agregado al carrito');
    } catch (err) {
      console.error('Error adding to cart:', err);
      alert('Error al agregar al carrito. Por favor, intenta de nuevo.');
    }
  };

  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };
  
  const handleSearch = (e) => {
    e.preventDefault();
    // Search happens in useEffect when searchTerm changes
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Productos</h1>
      
      {/* Search and filters */}
      <div className="mb-8 bg-gray-100 p-4 rounded-lg">
        <div className="flex flex-col md:flex-row gap-4">
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <input
                type="text"
                placeholder="Buscar productos..."
                className="w-full p-2 border border-gray-300 rounded-md"
                value={searchTerm}
                onChange={handleSearchChange}
              />
              <button
                type="submit"
                className="absolute right-0 top-0 h-full px-4 bg-gray-200 rounded-r-md border-l border-gray-300"
              >
                Buscar
              </button>
            </div>
          </form>
          
          <div className="w-full md:w-64">
            <select
              className="w-full p-2 border border-gray-300 rounded-md"
              value={selectedCategory}
              onChange={handleCategoryChange}
            >
              <option value="">Todas las categorías</option>
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.nombre}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Products grid */}
      {loading ? (
        <div className="text-center py-16">
          <p className="text-gray-500">Cargando productos...</p>
        </div>
      ) : error ? (
        <div className="text-center py-16 text-red-500">
          <p>{error}</p>
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-gray-500">No se encontraron productos</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map(product => (
            <div key={product.id} className="border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm hover:shadow-md transition-shadow">
              <a href={`/products/${product.id}`}>
                <img
                  src={product.url_imagen || 'https://via.placeholder.com/300x300?text=No+Image'}
                  alt={product.nombre}
                  className="w-full h-48 object-cover"
                />
              </a>
              <div className="p-4">
                <a href={`/products/${product.id}`} className="block">
                  <h2 className="text-lg font-semibold text-gray-800 mb-1">{product.nombre}</h2>
                  <p className="text-sm text-gray-600 mb-2">{product.categoria_nombre}</p>
                </a>
                
                <div className="flex justify-between items-center mt-4">
                  <div>
                    {product.precio_descuento ? (
                      <>
                        <span className="text-lg font-bold text-gray-800">${product.precio_descuento}</span>
                        <span className="text-sm text-gray-500 line-through ml-2">${product.precio}</span>
                      </>
                    ) : (
                      <span className="text-lg font-bold text-gray-800">${product.precio}</span>
                    )}
                  </div>
                  <button
                    onClick={() => handleAddToCart(product.id)}
                    className="bg-gray-700 text-white px-3 py-1 rounded-md text-sm hover:bg-gray-600"
                  >
                    Agregar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductList;