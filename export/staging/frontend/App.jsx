import React, { useState, useEffect } from 'react';

export default function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In production, connects to AWS ALB endpoint
    fetch('http://localhost:8000/api/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data);
        setLoading(false);
      })
      .catch(err => {
        console.warn("Backend offline, using fallback products", err);
        setProducts([
          { id: '1', title: 'Cloud Edge AI Compute Stick', price: 7499.0, category: 'Hardware' },
          { id: '2', title: 'Ergonomic DevOps Keyboard', price: 12999.0, category: 'Accessories' }
        ]);
        setLoading(false);
      });
  }, []);

  const addToCart = (product) => {
    setCart([...cart, product]);
  };

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '24px', maxWidth: '1000px', margin: '0 auto' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #e5e7eb', paddingBottom: '16px' }}>
        <h1 style={{ color: '#2563eb', margin: 0 }}>AI-Generated Cloud E-Commerce Store</h1>
        <div style={{ fontWeight: 'bold' }}>🛒 Cart: {cart.length} items</div>
      </header>
      <main style={{ marginTop: '24px' }}>
        <h2>Available Products (Live from FastAPI + PostgreSQL)</h2>
        {loading ? <p>Loading catalog...</p> : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px', marginTop: '16px' }}>
            {products.map(p => (
              <div key={p.id} style={{ border: '1px solid #d1d5db', borderRadius: '8px', padding: '16px', backgroundColor: '#f9fafb' }}>
                <h3 style={{ margin: '0 0 8px 0' }}>{p.title}</h3>
                <p style={{ color: '#4b5563', margin: '0 0 12px 0' }}>Category: {p.category}</p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#059669' }}>₹{p.price}</span>
                  <button 
                    onClick={() => addToCart(p)}
                    style={{ backgroundColor: '#2563eb', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    Add to Cart
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
