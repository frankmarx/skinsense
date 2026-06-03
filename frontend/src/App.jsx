import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { AdminPanel } from './pages/AdminPage';
import { PriceGrid as DashboardPage } from './pages/DashboardPage';

export default function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [showAdmin, setShowAdmin] = useState(false);
  const [logs, setLogs] = useState([]);
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('name-asc');

  const eventList = [
    { name: 'Sync Item Listings', action: 'cs_float_item_listings' },
    { name: 'Test CSFloat Connection', action: 'cs_float_test_connection' }
  ];

  const triggerEvent = async (action) => {
    if (!window.confirm(`Trigger ${action}?`)) return;
    const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
    await fetch(`${apiBaseUrl}/events/sync`, { 
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
  };

  const fetchLogs = async () => {
    const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
    const response = await fetch(`${apiBaseUrl}/logs`);
    const data = await response.json();
    setLogs(data.logs);
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <div className="app-container">
      <Header theme={theme} toggleTheme={() => setTheme(t => t === 'light' ? 'dark' : 'light')} setShowAdmin={setShowAdmin} />
      {showAdmin ? (
        <AdminPanel eventList={eventList} triggerEvent={triggerEvent} logs={logs} />
      ) : (
        <DashboardPage 
          prices={prices} 
          loading={loading} 
          searchQuery={searchQuery} 
          setSearchQuery={setSearchQuery}
          sortBy={sortBy}
          setSortBy={setSortBy}
        />
      )}
    </div>
  );
}
