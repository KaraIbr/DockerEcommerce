import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Layout components
import Navbar from './components/layout/Navbar';

// Auth components
import Login from './components/auth/Login';
import Register from './components/auth/Register';

// Product components
import ProductList from './components/products/ProductList';
import ProductDetail from './components/products/ProductDetail';

// Cart components
import Cart from './components/cart/Cart';

function App() {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    // Check if user is logged in on app load
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    
    // Listen for authentication changes
    const handleStorageChange = () => {
      const updatedUser = localStorage.getItem('user');
      if (updatedUser) {
        setUser(JSON.parse(updatedUser));
      } else {
        setUser(null);
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        <Navbar />
        <main>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
            <Route path="/register" element={user ? <Navigate to="/" /> : <Register />} />
            
            {/* Product routes */}
            <Route path="/" element={<ProductList />} />
            <Route path="/products" element={<ProductList />} />
            <Route path="/products/:id" element={
              <RouteWithParams component={ProductDetail} paramName="productId" />
            } />
            
            {/* Protected routes */}
            <Route path="/cart" element={user ? <Cart /> : <Navigate to="/login" />} />
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

// Helper component to pass route params as props
function RouteWithParams({ component: Component, paramName }) {
  const params = window.location.pathname.split('/');
  const paramValue = params[params.length - 1];
  
  const props = {
    [paramName]: paramValue
  };
  
  return <Component {...props} />;
}

export default App;
