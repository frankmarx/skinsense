import React, { useState, useEffect } from 'react';

export default function App() {
  // Theme state: default to 'dark' for a premium gaming look, but completely toggleable!
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved || 'dark';
  });

  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDummy, setIsDummy] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('name-asc'); // name-asc, name-desc, price-asc, price-desc

  // Toggle theme and update HTML dataset
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Fetch prices from AWS Chalice backend
  const fetchPrices = async () => {
    setLoading(true);
    setError(null);
    try {
      const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiBaseUrl}/prices`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      if (result.status === 'success' && Array.isArray(result.data)) {
        setPrices(result.data);
        setIsDummy(!!result.is_dummy);
      } else {
        throw new Error('Invalid data format received from API');
      }
    } catch (err) {
      console.warn('Backend connection failed, loading fallback client-side dummy data. Error:', err.message);
      // Fallback local dummy data in case backend is offline during initial frontend prototype testing
      setPrices([
        { market_hash_name: "★ M9 Bayonet | Doppler (Factory New)", price: 1420.50, updated_at: new Date().toISOString() },
        { market_hash_name: "AK-47 | Case Hardened (Minimal Wear)", price: 380.00, updated_at: new Date().toISOString() },
        { market_hash_name: "AWP | Asiimov (Field-Tested)", price: 165.25, updated_at: new Date().toISOString() },
        { market_hash_name: "M4A1-S | Printstream (Field-Tested)", price: 210.80, updated_at: new Date().toISOString() },
        { market_hash_name: "★ Sport Gloves | Pandora's Box (Battle-Scarred)", price: 890.00, updated_at: new Date().toISOString() },
        { market_hash_name: "Glock-18 | Fade (Factory New)", price: 1150.00, updated_at: new Date().toISOString() },
        { market_hash_name: "Desert Eagle | Blaze (Factory New)", price: 620.45, updated_at: new Date().toISOString() },
        { market_hash_name: "★ Karambit | Marble Fade (Factory New)", price: 1580.00, updated_at: new Date().toISOString() }
      ]);
      setIsDummy(true);
      setError('Could not connect to live Chalice backend. Displaying offline fallback mockup data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrices();
  }, []);

  // Filter and sort prices based on search input & selection
  const filteredPrices = prices
    .filter(item => item.market_hash_name.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === 'name-asc') return a.market_hash_name.localeCompare(b.market_hash_name);
      if (sortBy === 'name-desc') return b.market_hash_name.localeCompare(a.market_hash_name);
      if (sortBy === 'price-asc') return a.price - b.price;
      if (sortBy === 'price-desc') return b.price - a.price;
      return 0;
    });

  return (
    <div style={styles.appContainer}>
      {/* HEADER NAVBAR */}
      <header style={styles.header}>
        <div style={styles.logoContainer}>
          <span style={styles.logoIcon}>🏷️</span>
          <span style={styles.logoText}>skinsense</span>
        </div>
        
        <div style={styles.headerActions}>
          {/* Light/Dark Toggle */}
          <button 
            onClick={toggleTheme} 
            style={styles.themeButton}
            title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
            aria-label="Toggle Theme"
          >
            {theme === 'light' ? (
              // Moon Icon
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
              </svg>
            ) : (
              // Sun Icon
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
              </svg>
            )}
          </button>

          {/* User Placeholder */}
          <button style={styles.userButton} title="User Profile" aria-label="User Profile">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </button>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main style={styles.main}>
        {/* Intro Dashboard Row */}
        <section style={styles.introSection}>
          <div>
            <h2 style={styles.pageTitle}>CS2 Price Aggregator</h2>
            <p style={styles.pageSubtitle}>High-fidelity marketplace index and real-time pricing analysis.</p>
          </div>
          
          {/* Status Badge */}
          <div style={styles.statusContainer}>
            {isDummy ? (
              <span style={{ ...styles.badge, ...styles.badgeWarning }}>
                <span className="pulse-dot" style={styles.pulseDot}></span> Demo Mock Data
              </span>
            ) : (
              <span style={{ ...styles.badge, ...styles.badgeSuccess }}>
                ● Connected to AWS Chalice DB
              </span>
            )}
            
            <button onClick={fetchPrices} style={styles.refreshButton} disabled={loading}>
              <svg 
                className={loading ? "spinner" : ""}
                width="14" 
                height="14" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2.5" 
                style={{ marginRight: '6px' }}
              >
                <path d="M23 4v6h-6"></path>
                <path d="M1 20v-6h6"></path>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
              </svg>
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </section>

        {/* API Warning banner */}
        {error && (
          <div style={styles.warningBanner}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '8px', flexShrink: 0 }}>
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <span>{error}</span>
            </div>
            <span style={styles.subtleText}>To start backend, run <code>chalice local</code> in <code>backend/</code>.</span>
          </div>
        )}

        {/* CONTROLS BAR (Search & Sort) */}
        <section style={styles.controlsSection}>
          <div style={styles.searchWrapper}>
            <svg style={styles.searchIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input 
              type="text" 
              placeholder="Search CS2 skin or knife name..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={styles.searchInput}
            />
          </div>

          <div style={styles.sortWrapper}>
            <span style={styles.sortLabel}>Sort By:</span>
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              style={styles.sortSelect}
            >
              <option value="name-asc">Alphabetical (A-Z)</option>
              <option value="name-desc">Alphabetical (Z-A)</option>
              <option value="price-desc">Price: High to Low</option>
              <option value="price-asc">Price: Low to High</option>
            </select>
          </div>
        </section>

        {/* DATA GRID */}
        {loading ? (
          <div style={styles.loadingContainer}>
            <div className="spinner" style={styles.spinner}></div>
            <p style={{ marginTop: '16px', color: 'var(--text-secondary)', fontSize: '14px' }}>Querying price records...</p>
          </div>
        ) : filteredPrices.length === 0 ? (
          <div style={styles.emptyContainer}>
            <p>No item records matched your search filter.</p>
          </div>
        ) : (
          <div style={styles.grid}>
            {filteredPrices.map((item, index) => {
              // Extract styling values based on skin names
              const isKnife = item.market_hash_name.includes('★');
              const isCovert = item.market_hash_name.includes('Fade') || item.market_hash_name.includes('Doppler') || item.market_hash_name.includes('Printstream');
              
              const accentBorder = isKnife 
                ? '2px solid #eab308' // Gold accent for high rarity knives
                : isCovert 
                ? '2px solid #ec4899' // Pink/Red for covert weapons
                : '2px solid var(--border-color)';

              return (
                <div key={index} style={{ ...styles.card, borderTop: accentBorder }}>
                  <div style={styles.cardHeader}>
                    <span style={styles.rarityLabel}>
                      {isKnife ? '★ Rare Special Item' : isCovert ? 'Covert Grade' : 'Classified Grade'}
                    </span>
                    <span style={styles.currencyBadge}>USD</span>
                  </div>
                  
                  <h3 style={styles.itemName}>{item.market_hash_name}</h3>
                  
                  <div style={styles.cardFooter}>
                    <div style={styles.priceContainer}>
                      <span style={styles.priceLabel}>Current Price</span>
                      <span style={styles.priceValue}>
                        ${item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </span>
                    </div>
                    
                    <div style={styles.timeContainer}>
                      <span style={styles.timeLabel}>Updated</span>
                      <span style={styles.timeValue}>
                        {new Date(item.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* FOOTER */}
      <footer style={styles.footer}>
        <p>© {new Date().getFullYear()} skinsense • Serverless CS2 Price Matrix Boilerplate</p>
      </footer>
    </div>
  );
}

// Minimalist, robust, theme-responsive styling using inline JS CSS properties
const styles = {
  appContainer: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: 'var(--bg-primary)',
    color: 'var(--text-primary)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '14px 24px',
    backgroundColor: 'var(--bg-secondary)',
    borderBottom: '1px solid var(--border-color)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  logoContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  logoIcon: {
    fontSize: '20px',
  },
  logoText: {
    fontSize: '18px',
    fontWeight: 700,
    letterSpacing: '-0.025em',
  },
  headerActions: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  themeButton: {
    background: 'none',
    border: '1px solid var(--border-color)',
    borderRadius: '8px',
    width: '36px',
    height: '36px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    color: 'var(--text-primary)',
    backgroundColor: 'var(--bg-primary)',
  },
  userButton: {
    background: 'none',
    border: '1px solid var(--border-color)',
    borderRadius: '8px',
    width: '36px',
    height: '36px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    color: 'var(--text-primary)',
    backgroundColor: 'var(--bg-primary)',
  },
  main: {
    flex: 1,
    width: '100%',
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '32px 24px',
  },
  introSection: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '16px',
    marginBottom: '28px',
  },
  pageTitle: {
    fontSize: '24px',
    fontWeight: 700,
    letterSpacing: '-0.02em',
    marginBottom: '2px',
  },
  pageSubtitle: {
    color: 'var(--text-secondary)',
    fontSize: '14px',
  },
  statusContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '6px 12px',
    borderRadius: '20px',
    fontSize: '13px',
    fontWeight: 500,
    gap: '6px',
  },
  badgeSuccess: {
    backgroundColor: 'rgba(34, 197, 94, 0.1)',
    color: '#22c55e',
  },
  badgeWarning: {
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    color: '#f59e0b',
  },
  pulseDot: {
    width: '6px',
    height: '6px',
    backgroundColor: '#f59e0b',
    borderRadius: '50%',
    display: 'inline-block',
  },
  refreshButton: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '7px 12px',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
    backgroundColor: 'var(--bg-secondary)',
    color: 'var(--text-primary)',
    fontSize: '13px',
    fontWeight: 500,
    cursor: 'pointer',
  },
  warningBanner: {
    backgroundColor: 'rgba(239, 68, 68, 0.05)',
    border: '1px solid rgba(239, 68, 68, 0.15)',
    color: '#ef4444',
    padding: '10px 14px',
    borderRadius: '8px',
    marginBottom: '28px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '13px',
    flexWrap: 'wrap',
    gap: '8px',
  },
  controlsSection: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '16px',
    marginBottom: '24px',
    flexWrap: 'wrap',
  },
  searchWrapper: {
    position: 'relative',
    flex: '1',
    minWidth: '260px',
    maxWidth: '440px',
  },
  searchIcon: {
    position: 'absolute',
    left: '12px',
    top: '50%',
    transform: 'translateY(-50%)',
    color: 'var(--text-secondary)',
    opacity: 0.8,
  },
  searchInput: {
    width: '100%',
    padding: '10px 12px 10px 38px',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
    backgroundColor: 'var(--bg-secondary)',
    color: 'var(--text-primary)',
    fontSize: '14px',
    outline: 'none',
  },
  sortWrapper: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  sortLabel: {
    fontSize: '13px',
    color: 'var(--text-secondary)',
  },
  sortSelect: {
    padding: '8px 12px',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
    backgroundColor: 'var(--bg-secondary)',
    color: 'var(--text-primary)',
    fontSize: '13px',
    outline: 'none',
    cursor: 'pointer',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
    gap: '20px',
  },
  card: {
    backgroundColor: 'var(--bg-secondary)',
    borderRadius: '10px',
    padding: '18px',
    border: '1px solid var(--border-color)',
    boxShadow: 'var(--card-shadow)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    gap: '14px',
    minHeight: '150px',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  rarityLabel: {
    fontSize: '10px',
    fontWeight: 600,
    textTransform: 'uppercase',
    color: 'var(--text-secondary)',
    letterSpacing: '0.04em',
  },
  currencyBadge: {
    fontSize: '9px',
    fontWeight: 700,
    backgroundColor: 'var(--bg-primary)',
    padding: '1px 5px',
    borderRadius: '4px',
    color: 'var(--text-secondary)',
  },
  itemName: {
    fontSize: '15px',
    fontWeight: 600,
    lineHeight: '1.4',
    color: 'var(--text-primary)',
  },
  cardFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    paddingTop: '10px',
    borderTop: '1px dashed var(--border-color)',
  },
  priceContainer: {
    display: 'flex',
    flexDirection: 'column',
  },
  priceLabel: {
    fontSize: '10px',
    color: 'var(--text-secondary)',
  },
  priceValue: {
    fontSize: '16px',
    fontWeight: 700,
    color: 'var(--text-primary)',
  },
  timeContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
  },
  timeLabel: {
    fontSize: '10px',
    color: 'var(--text-secondary)',
  },
  timeValue: {
    fontSize: '11px',
    color: 'var(--text-secondary)',
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '50px 0',
  },
  spinner: {
    width: '32px',
    height: '32px',
    border: '3px solid var(--border-color)',
    borderTop: '3px solid var(--accent-color)',
    borderRadius: '50%',
  },
  emptyContainer: {
    textAlign: 'center',
    padding: '40px 0',
    color: 'var(--text-secondary)',
    backgroundColor: 'var(--bg-secondary)',
    borderRadius: '10px',
    border: '1px solid var(--border-color)',
  },
  subtleText: {
    fontSize: '11px',
    opacity: 0.8,
  },
  footer: {
    textAlign: 'center',
    padding: '30px 24px',
    borderTop: '1px solid var(--border-color)',
    backgroundColor: 'var(--bg-secondary)',
    color: 'var(--text-secondary)',
    fontSize: '12px',
    marginTop: '60px',
  }
};
