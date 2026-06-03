import React from 'react';

export const PriceGrid = ({ prices, loading, error, fetchPrices, searchQuery, setSearchQuery, sortBy, setSortBy }) => (
  <main>
    <section>
      <h2>CS2 Price Aggregator</h2>
      <button onClick={fetchPrices}>Refresh</button>
      <input type="text" placeholder="Search..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
    </section>
    {loading ? <p>Loading...</p> : (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
        {prices.map((item, index) => (
          <div key={index} style={{ border: '1px solid #ccc', padding: '10px' }}>
            <h3>{item.market_hash_name}</h3>
            <p>${item.price}</p>
          </div>
        ))}
      </div>
    )}
  </main>
);
