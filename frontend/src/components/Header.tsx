import React from 'react';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo">QB</div>
          <div className="title-section">
            <h1>QuickBooks Commerce</h1>
            <p>Sales Forecasting Dashboard</p>
          </div>
        </div>
        <div className="header-info">
          <span className="status-badge">
            <span className="status-dot"></span>
            Live
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
