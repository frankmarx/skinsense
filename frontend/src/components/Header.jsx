import React from 'react';

export const Header = ({ theme, toggleTheme, setShowAdmin }) => (
  <header style={styles.header}>
    <div style={styles.logoContainer}>
      <span style={styles.logoIcon}>🏷️</span>
      <span style={styles.logoText}>skinsense</span>
    </div>
    <div style={styles.headerActions}>
      <button onClick={toggleTheme} style={styles.themeButton}>
        {theme === 'light' ? '🌙' : '☀️'}
      </button>
      <button onClick={() => setShowAdmin(prev => !prev)} style={styles.themeButton}>
        ⚙️
      </button>
    </div>
  </header>
);

const styles = {
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 24px', backgroundColor: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-color)' },
  logoContainer: { display: 'flex', alignItems: 'center', gap: '8px' },
  logoIcon: { fontSize: '20px' },
  logoText: { fontSize: '18px', fontWeight: 700 },
  headerActions: { display: 'flex', gap: '12px' },
  themeButton: { background: 'none', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '8px', cursor: 'pointer' },
};
