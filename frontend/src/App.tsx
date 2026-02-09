import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import { ForecastService } from './services/api';

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check API health on mount
    const checkHealth = async () => {
      try {
        const service = new ForecastService();
        await service.healthCheck();
        setLoading(false);
      } catch (err) {
        setError('Unable to connect to API. Please ensure the backend is running.');
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  if (loading) {
    return (
      <div className="App">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading QuickBooks Commerce Forecasting...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="error-container">
          <h2>Connection Error</h2>
          <p>{error}</p>
          <p className="error-hint">
            Start the backend: <code>cd backend && python -m app.main</code>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Header />
      <Dashboard />
    </div>
  );
}

export default App;
