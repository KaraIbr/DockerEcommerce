import React, { useState, useEffect } from 'react';

const Navbar = () => {
  const [user, setUser] = useState(null);
  const [cartItemsCount, setCartItemsCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  
  useEffect(() => {
    // Check if user is logged in
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    
    // Check cart items count
    const updateCartCount = () => {
      const storedUser = localStorage.getItem('user');
      if (!storedUser) return;
      
      const user = JSON.parse(storedUser);
      
      fetch(`http://localhost:5000/carrito?usuario_id=${user.id}`)
        .then(res => res.json())
        .then(data => {
          if (data.resumen) {
            setCartItemsCount(data.resumen.total_items || 0);
          }
        })
        .catch(err => console.error('Error fetching cart:', err));
    };
    
    // Initial cart count
    updateCartCount();
    
    // Listen for cart updates
    window.addEventListener('cartUpdated', updateCartCount);
    
    return () => {
      window.removeEventListener('cartUpdated', updateCartCount);
    };
  }, []);
  
  const handleLogout = () => {
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container container">
        <div className="nav-logo">
          <a href="/" className="nav-link">Luna Pharmacy</a>
        </div>
        
        <div className="nav-links">
          <a href="/" className="nav-link">Inicio</a>
          <a href="/products" className="nav-link">Productos</a>
          
          {user ? (
            <>
              <a href="/cart" className="nav-link" style={{ position: 'relative' }}>
                Carrito
                {cartItemsCount > 0 && (
                  <span style={{
                    position: 'absolute',
                    top: '-8px',
                    right: '-8px',
                    backgroundColor: '#e53e3e',
                    color: 'white',
                    borderRadius: '50%',
                    width: '18px',
                    height: '18px',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {cartItemsCount}
                  </span>
                )}
              </a>
              
              <div style={{ position: 'relative' }}>
                <button 
                  onClick={toggleDropdown}
                  className="nav-link" 
                  style={{ 
                    background: 'none', 
                    border: 'none', 
                    cursor: 'pointer',
                    color: 'white'
                  }}
                >
                  {user.nombre}
                </button>
                
                {showDropdown && (
                  <div style={{
                    position: 'absolute',
                    right: 0,
                    top: '100%',
                    width: '180px',
                    backgroundColor: 'white',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
                    zIndex: 10
                  }}>
                    <a 
                      href="/profile" 
                      style={{
                        display: 'block',
                        padding: '10px 15px',
                        color: '#333',
                        textDecoration: 'none'
                      }}
                    >
                      Perfil
                    </a>
                    <a 
                      href="/orders" 
                      style={{
                        display: 'block',
                        padding: '10px 15px',
                        color: '#333',
                        textDecoration: 'none'
                      }}
                    >
                      Mis Pedidos
                    </a>
                    <button 
                      onClick={handleLogout}
                      style={{
                        display: 'block',
                        width: '100%',
                        textAlign: 'left',
                        padding: '10px 15px',
                        color: '#333',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer'
                      }}
                    >
                      Cerrar Sesión
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <a href="/login" className="nav-link">Iniciar Sesión</a>
              <a 
                href="/register" 
                className="nav-link" 
                style={{ 
                  backgroundColor: '#555',
                  padding: '5px 10px',
                  borderRadius: '4px'
                }}
              >
                Registrarse
              </a>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;